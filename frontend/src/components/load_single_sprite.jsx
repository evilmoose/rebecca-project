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
        isTalking, 
        visemes,
        visemesIndex, 
        visemesStartTime 
    } = useSelector((state) => state.pixijs);
    const [baseDimensions] = useState({ width: 648, height: 900}); // Base dimensions for scaling


    // Refs for PixiJS app and container
    const containerRef = useRef(null);
    const appRef = useRef(null); // Ref to store the app instance

    // Texture storage for idle and talking animations
    const idleTextures = useRef([]); // Ref to store idle textures
    const talkingTextures = useRef({}); // Ref to store talking textures
    const rebecca = useRef(null); // Ref to store the sprite instance

    // animation tracking
    const idleFrameIndex = useRef(0); // Ref to store the current idle frame index
    // const elapsedIdleTime = useRef(0); // Ref to store the elapsed idle time
    const isBlinking = useRef(false); // Ref to store the blinking state
    const blinkFrameIndex = useRef(0); // Ref to store the current blink frame index

    useEffect(() => {
        console.log("PixiJS Container mounted - Initializing Pixijs Application...");
        
        // Initialize PixiJS Application
        const initializePixiJS = async () => {
            // Initialize PixiJS Application
            if (!appRef.current) {              
                console.log("Creating PixiJS Application...");
                // Create a new PixiJS Application
                appRef.current = new Application();
            
            
                // Initialize the Application with options
                await appRef.current.init({
                    resizeTo: containerRef.current,
                    background: "#ffffff",
                });
                
                console.log("PixiJS Application initialized.");
                // Store app in ref for later cleanup
                // appRef.current = app;

                // Append the canvas to the container
                if (containerRef.current) {
                    console.log("Appending canvas to container...");
                    containerRef.current.appendChild(appRef.current.canvas);
                }

                console.log("Loading textures...");

                // Load assets and map them into an array of textures
                const loadedIdleAssets = await Assets.load(rebecca_idle_textures);
                idleTextures.current = rebecca_idle_textures.map(
                    (path) => loadedIdleAssets[path]
                );

                // Load talking textures
                const loadedTalkingAssets = await Assets.load(
                    Object.values(rebecca_talking_textures)
                );
                Object.keys(rebecca_talking_textures).forEach((key) => {
                    talkingTextures.current [key] = loadedTalkingAssets[rebecca_talking_textures[key]];
                });

                console.log("Textures loaded successfully...");

                // Create and configure sprite
                rebecca.current = new Sprite(idleTextures.current[idleFrameIndex.current]);           
                rebecca.current.anchor.set(0.5);
                appRef.current.stage.addChild(rebecca.current);

                resizeCanvas();
            } // Initial canvas resize
        };
        initializePixiJS();

        // Resize Logic
        const resizeCanvas = () => {
            if (containerRef.current && appRef.current && appRef.current.renderer) {
                const { offsetWidth, offsetHeight } = containerRef.current;

                // Calculate scale factors based on the current size vs base size
                const scaleX = offsetWidth / baseDimensions.width;
                const scaleY = offsetHeight / baseDimensions.height;
                const scale = Math.min(scaleX, scaleY);

                // Apply scailng and repositioning
                rebecca.current.scale.set(scale);

                // Center the sprite
                rebecca.current.x = appRef.current.renderer.screen.width / 2;
                rebecca.current.y = appRef.current.renderer.screen.height / 2;

                // Ensure canvas is resized to container dimensions
                appRef.current.renderer.resize(offsetWidth, offsetHeight);
            }
        };

        // Force re-centering on maximize (additional logic for maximization)
        const handleMaximize = () => {
            setTimeout(() => {
                resizeCanvas(); // Force resizeCanvas call after maximize
            }, 50); // Slight delay to ensure browser resizing is complete
        };

        // Add resize listener
        window.addEventListener("resize", resizeCanvas);
        window.addEventListener("resize", handleMaximize);

        // Cleanup resize listener an unmount
        return () => {
            console.log("PixijsContainer unmounted - Cleaning up...");
            // Destroy PixiJS Application
            if (appRef.current) {
                console.log("Destroying PixiJS Application...");
                appRef.current.destroy(true, true);
                appRef.current = null;
            }
                
            window.removeEventListener("resize", resizeCanvas);
            window.removeEventListener("resize", handleMaximize);
            console.log("Cleanup complete...");
        };
    }, [baseDimensions.height, baseDimensions.width]); // Run only on mount and unmount

    useEffect(() => {
        // Ensure the app and sprite are initialized before adding the ticker
        //if (!rebecca.current || !appRef.current) {
            //console.warn("Sprite or appRef not initialized yet.");
            //return;
        //}
        
        const app = appRef.current;
        const sprite = rebecca.current;

        let elapsed = 0; // Elapsed time in milliseconds
        let desiredFPS = 8; // Set your desired FPS here (e.g., 8 or 30)
        let frameInterval = 1000 / desiredFPS; // Time in ms between frames

        const animationTicker = () => {
            console.log("Animation ticker running...");
            // Accumulate elapsed time in milliseconds
            elapsed += app.ticker.elapsedMS;

            if (isTalking && visemes && visemes.length > 0) {
                // Handle talking animation
                console.log("Talking animation active...");
                const currentTime = performance.now(); - visemesStartTime;

                if (visemesIndex < visemes.length) {
                    const viseme = visemes[visemesIndex];

                    // Check if it's time to switch to the next viseme
                    if (currentTime >= visemes.time) {
                        console.log(`Switching to viseme: ${viseme.value}`);
                        if (sprite.texture !== talkingTextures.current[viseme.value]) {
                            // Safely unload the current texture (if applicable)
                            console.log(`Unloading current texture: ${sprite.texture}`);
                            Assets.unload(sprite.texture);
                    
                            // Assign new texture
                            console.log(`Assigning new texture: ${talkingTextures.current[viseme.value]}`);
                            sprite.texture = 
                                talkingTextures.current[viseme.value] || 
                                talkingTextures.current["sil"];
                        }
                        dispatch(setVisemesIndex(visemesIndex + 1));
                    }
                } else {
                    // Talking animation is done
                    console.log("Talking animation completed. Resetting to idle frame.");
                    dispatch(setIsTalking(false));
                    dispatch(setVisemesIndex(0));
                    dispatch(setVisemesStartTime(0));
                            
                    // Safely reset to idle texture
                    if (sprite.texture !== idleTextures.current[idleFrameIndex.current]) {
                        console.log(`Unloading talking texture: ${sprite.texture}`);
                        Assets.unload(sprite.texture); // Unload the talking texture

                        console.log(`Assigning idle texture: ${idleTextures.current[idleFrameIndex.current]}`);
                        sprite.texture = idleTextures.current[idleFrameIndex.current]; // Assign idle frame
                    }
                }
            } else {
                // Check if enough time has passed to update the frame
                if (elapsed >= frameInterval) {
                    elapsed = 0; // Reset the elapsed time

                    if (isBlinking.current) {
                        // Handle blinking frames
                        blinkFrameIndex.current++;

                        if (blinkFrameIndex.current >= 3) {
                            isBlinking.current = false;
                            blinkFrameIndex.current = 0;
                        } else {
                            sprite.texture = idleTextures.current[idleFrameIndex.current + blinkFrameIndex.current];
                            console.log("Blinking frame:", blinkFrameIndex.current);
                        }
                    } else {
                        // Handle idle animation
                        idleFrameIndex.current = 
                            (idleFrameIndex.current + 1) % idleTextures.current.length;
                        
                        sprite.texture = idleTextures.current[idleFrameIndex.current];
                        console.log("Idle frame:", idleFrameIndex.current);

                        // Randomly trigger blinking
                        if (Math.random() < 0.02) { // 2% chance per frame
                            isBlinking.current = true;
                            blinkFrameIndex.current = 0;
                        }
                    }
                }
            }
        };

        appRef.current.ticker.add(animationTicker);

        // Cleanup to prevent memory leaks
        return () => {
            console.log("Removing animation ticker...");
            app.ticker.remove(animationTicker);
        };
    }, [dispatch, isTalking, visemes, visemesIndex, visemesStartTime]);

    return (
        <div
        id="pixijs-container"
        className="border p-3"
        ref={containerRef}>

        </div>
    );
};

export default PixijsContainer;
