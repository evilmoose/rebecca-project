import { useState, useEffect, useRef } from "react";
import { useSelector, useDispatch } from 'react-redux';
import { setIsTalking, setVisemesIndex, setVisemesStartTime } from '../store/slices/pixijsSlice';
import { Application, Assets, Sprite} from "pixi.js";
import rebecca_idle_textures from "../assets/rebecca_idle_textures";
import rebecca_talking_textures from "../assets/rebecca_talking_textures";

const PixijsContainer = () => {
    // Redux state selectors
    const dispatch = useDispatch();
    const { 
        isTalking: isTalkingRef, 
        visemes,
        visemesIndex: visemeIndexRef, 
        visemesStartTime: visemeStartTimeRef } = useSelector((state) => state.pixijs);
    // Refs to store state values    
    const containerRef = useRef(null);
    const appRef = useRef(null); // Ref to store the app instance
    const [baseDimensions] = useState({ width: 648, height: 900}); // Base dimensions for scaling

    useEffect(() => {

        // Array to store loaded textures
        let idleTextures = [];
        let talkingTextures = [];

        // Sprite reference for resizing and scaling
        let rebecca;

        let elapsed = 0; // Accumulated time in milliseconds
        let currentFrameIndex = 0; // Index for idle frames
        let blinkFrameIndex = 0; // Index for blink frames
        let isBlinking = false; // State to track blinking

        if (!appRef.current) {
            console.log("Creating PixiJS Application...");
            // Create a new PixiJS Application
            const app = new Application();
            
            (async () => {
                // Initialize the Application with options
                await app.init({
                    resizeTo: containerRef.current,
                    background: "#ffffff",
                });
                
                console.log("PixiJS Application initialized.");
                // Store app in ref for later cleanup
                appRef.current = app;

                // Append the canvas to the container
                if (containerRef.current) {
                    console.log("Appending canvas to container...");
                    console.log(containerRef.current)
                    containerRef.current.appendChild(app.canvas);
                }

                // Load assets and map them into an array of textures
                const loadedIdleAssets = await Assets.load(rebecca_idle_textures);
                idleTextures = rebecca_idle_textures.map((path) => loadedIdleAssets[path]);

                // Load talking textures
                const loadedTalkingAssets = await Assets.load(Object.values(rebecca_talking_textures));
                Object.keys(rebecca_talking_textures).forEach((key) => {
                    talkingTextures[key] = loadedTalkingAssets[rebecca_talking_textures[key]];
                });

                // Create a sprite and set the first texture
                rebecca = new Sprite(idleTextures[currentFrameIndex]);           

                // Center the sprite's anchor point
                rebecca.anchor.set(0.5);

                // Add to stage
                app.stage.addChild(rebecca);

                let desiredFPS = 8; // Set your desired FPS here (e.g., 8 or 30)
                let frameInterval = 1000 / desiredFPS; // Time in ms between frames

                app.ticker.add((/*delta*/) => {
                    console.log("Animation ticker running...");
                    // Accumulate elapsed time in milliseconds
                    elapsed += app.ticker.elapsedMS;

                    if (isTalkingRef && visemes && visemes.length > 0) {
                        // Handle talking animation
                        console.log("Talking animation active...");
                        const currentTime = performance.now(); - visemeStartTimeRef.current;

                        if (visemeIndexRef.current < visemes.length) {
                            const viseme = visemes[visemeIndexRef.current];

                            // Check if it's time to switch to the next viseme
                            if (currentTime >= visemes.time) {
                                console.log(`Switching to viseme: ${viseme.value}`);
                                if (rebecca.texture !== talkingTextures[viseme.value]) {
                                    // Safely unload the current texture (if applicable)
                                    console.log(`Unloading current texture: ${rebecca.texture}`);
                                    Assets.unload(rebecca.texture);
                    
                                    // Assign new texture
                                    console.log(`Assigning new texture: ${talkingTextures[viseme.value]}`);
                                    rebecca.texture = talkingTextures[viseme.value] || talkingTextures["sil"];
                                }
                                dispatch(setVisemesIndex(visemeIndexRef.current + 1));
                            }
                        } else {
                            // Talking animation is done
                            console.log("Talking animation completed. Resetting to idle frame.");
                            dispatch(setIsTalking(false));
                            dispatch(setVisemesIndex(0));
                            dispatch(setVisemesStartTime(0));
                            // Safely reset to idle texture
                            if (rebecca.texture !== idleTextures[currentFrameIndex]) {
                                console.log(`Unloading talking texture: ${rebecca.texture}`);
                                Assets.unload(rebecca.texture); // Unload the talking texture

                                console.log(`Assigning idle texture: ${idleTextures[currentFrameIndex]}`);
                                rebecca.texture = idleTextures[currentFrameIndex]; // Assign idle frame
                            }
                        }
                    } else {
                        // Check if enough time has passed to update the frame
                        if (elapsed >= frameInterval) {
                            elapsed = 0; // Reset the elapsed time

                            if (isBlinking) {
                                console.log("Blinking animation started...")
                                // Handle blinking frames
                                blinkFrameIndex++;
                                if (blinkFrameIndex >= 3) {
                                    isBlinking = false;
                                    blinkFrameIndex = 0;
                                    currentFrameIndex = (currentFrameIndex + 3) % idleTextures.length;
                                }
                                rebecca.texture = idleTextures[currentFrameIndex + blinkFrameIndex];
                            } else {
                                console.log("Idle animation started...")
                                // Handle idle animation
                                currentFrameIndex = (currentFrameIndex + 3) % idleTextures.length;
                                rebecca.texture = idleTextures[currentFrameIndex];
                                // Randomly trigger blinking
                                if (Math.random() < 0.02) { // 2% chance per frame
                                    isBlinking = true;
                                }
                            }
                        }
                    }
                });
                // Handle resizing
                const resizeCanvas = () => {
                    if (containerRef.current) {
                        const { offsetWidth, offsetHeight } = containerRef.current;

                        // Calculate scale factors based on the current size vs base size
                        const scaleX = offsetWidth / baseDimensions.width;
                        const scaleY = offsetHeight / baseDimensions.height;
                        const scale = Math.min(scaleX, scaleY);

                        // Apply scailng and repositioning
                        rebecca.scale.set(scale);

                        // Center the sprite
                        rebecca.x = app.renderer.screen.width / 2;
                        rebecca.y = app.renderer.screen.height / 2;

                        // Ensure canvas is resized to container dimensions
                        app.renderer.resize(offsetWidth, offsetHeight);
                    }
                };
               
                // Add resize listener
                window.addEventListener("resize", resizeCanvas);
                resizeCanvas();

                // Force re-centering on maximize (additional logic for maximization)
                const handleMaximize = () => {
                    setTimeout(() => {
                        resizeCanvas(); // Force resizeCanvas call after maximize
                    }, 50); // Slight delay to ensure browser resizing is complete
                };

                // Add maximize detection (resize listener should already catch this)
                window.addEventListener("resize", handleMaximize);
                

                // Cleanup resize listener an unmount
                return () => {
                    window.removeEventListener("resize", resizeCanvas);
                    window.removeEventListener("resize", handleMaximize);
                };
            })();

            // Store app in ref for cleanup
            appRef.current = app;
        }
        // Cleanup to prevent memory leaks
        return () => {
            console.log("Cleaning up PixiJS container...");
            // Unload textures before destroying the application
            if (idleTextures.length > 0) {
                console.log("Unloading idle textures...");
                Assets.unload(rebecca_idle_textures); // Properly unload idle textures
            }

            if (Object.keys(rebecca_talking_textures).length > 0) {
                console.log("Unloading talking textures...");
                Assets.unload(Object.values(rebecca_talking_textures)); // Unload talking textures
            }

            if (appRef.current) {
                console.log("Destroying PixiJS Application...");
                appRef.current.destroy(true, true);
                appRef.current = null;
            }
            console.log("Cleanup complete.");
        };
},[baseDimensions, dispatch, isTalkingRef, visemes, visemeIndexRef, visemeStartTimeRef]);

    return (
        <div
        id="pixijs-container"
        className="border p-3"
        ref={containerRef}>

        </div>
    );
};

export default PixijsContainer;
