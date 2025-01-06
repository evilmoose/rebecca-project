import { useState, useEffect, useRef } from "react";
import { Application, Assets, Sprite} from "pixi.js";
import rebecca_textures from "../assets/rebecca_textures";

const PixijsContainer = () => {
    const containerRef = useRef(null);
    const appRef = useRef(null); // Ref to store the app instance
    const [baseDimensions] = useState({ width: 648, height: 900}); // Base dimensions for scaling

    useEffect(() => {

        // Array to store loaded textures
        let textures = [];

        // Sprite reference for resizing and scaling
        let rebecca;

        if (!appRef.current) {
            // Create a new PixiJS Application
            const app = new Application();
            
            (async () => {
                // Initialize the Application with options
                await app.init({
                    resizeTo: containerRef.current,
                    background: "#ffffff",
                });

                // Store app in ref for later cleanup
                appRef.current = app;

                // Append the canvas to the container
                if (containerRef.current) {
                    containerRef.current.appendChild(app.canvas);
                }
                
                // Load am array of textures.
                const texturePaths = rebecca_textures;

                // Load assets and map them into an array of textures
                const loadedAssets = await Assets.load(texturePaths);
                textures = texturePaths.map((path) => loadedAssets[path]);

                // Create a sprite and set the first texture
                let currentFrameIndex = 0;
                rebecca = new Sprite(textures[currentFrameIndex]);          

                // Center the sprite's anchor point
                rebecca.anchor.set(0.5);

                // Move the sprite to the center of the screen
                //rebecca.x = app.screen.width / 2;
                //rebecca.y = app.screen.height / 2;

                // Add to stage
                app.stage.addChild(rebecca);

                let elapsed = 0; // Accumulated time in milliseconds
                let desiredFPS = 16; // Set your desired FPS here (e.g., 8 or 30)
                let frameInterval = 1000 / desiredFPS; // Time in ms between frames

                app.ticker.add((/*delta*/) => {
                    // Accumulate elapsed time in milliseconds
                    elapsed += app.ticker.elapsedMS;

                    // Check if enough time has passed to update the frame
                    if (elapsed >= frameInterval) {
                        elapsed = 0; // Reset the elapsed time
                        currentFrameIndex = (currentFrameIndex + 1) % textures.length; // Update the frame index
                        rebecca.texture = textures[currentFrameIndex]; // Change the sprite texture
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
            if (appRef.current) {
                appRef.current.destroy(true, true);
                appRef.current = null;
            }

            if (textures.length > 0) {
                Assets.unload(rebecca_textures); // Unload the textures
            }
        };
},[baseDimensions]);

    return (
        <div
        id="pixijs-container"
        className="border p-3"
        ref={containerRef}>

        </div>
    )
};

export default PixijsContainer;
