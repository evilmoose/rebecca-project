import { useEffect, useRef } from "react";
import { Application, Assets, Sprite} from "pixi.js";

const ThreeJSContainer = () => {
    const containerRef = useRef(null);
    const appRef = useRef(null); // Ref to store the app instance

    useEffect(() => {
        if (!appRef.current) {
            // Create a new PixiJS Application
            const app = new Application();
            
            (async () => {
                // Initialize the Application with options
                await app.init({
                    width: 648,
                    height: 900,
                    background: "#1099bb",
                });

                
                // Store app in ref for later cleanup
                appRef.current = app;

                // Append the canvas to the container
                if (containerRef.current) {
                    containerRef.current.appendChild(app.canvas);
                }
                
                // Load the bunny texture.
                const texture = await Assets.load('/rebecca_neutral.png');

                // Create a new Sprite from an image path
                const rebecca = new Sprite(texture);           

                // Center the sprite's anchor point
                rebecca.anchor.set(0.5);

                // Move the sprite to the center of the screen
                rebecca.x = app.screen.width / 2;
                rebecca.y = app.screen.height / 2;

                // Add to stage
                app.stage.addChild(rebecca);
            })();
        }
        // Cleanup to prevent memory leaks
        // Cleanup on unmount
        return () => {
            if (appRef.current) {
                appRef.current.destroy(true, true);
                appRef.current = null;
            }
        };
}, []);

    return (
        <div
        id="threejs-container"
        className="border p-3"
        ref={containerRef}>

        </div>
    )
};

export default ThreeJSContainer;
