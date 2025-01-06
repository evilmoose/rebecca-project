import { useEffect, useRef } from "react";
import { Application, Assets, Sprite, Rectangle, Texture } from "pixi.js";

const ThreeJSContainer = () => {
    const containerRef = useRef(null);
    const appRef = useRef(null);

    useEffect(() => {
      if (!appRef.current) {
        (async () => {
            // Create a new PixiJS Application
            const app = new Application();

            // Initialize the Application with options
            await app.init({
                resizeTo: window,
                background: "#1099bb", // Set background color
                antialias: true, // Smooth rendering
            });

            // Save the Application instance
            appRef.current = app;

            // Append the canvas to the DOM
            containerRef.current.appendChild(app.canvas);

            // Load the sprite sheet
            const spriteSheetPath = "/sprite_sheet.png"; // Update with the actual path
            const texture = await Assets.load(spriteSheetPath);

            // Define frame dimensions and extract frames
            const frameWidth = 648;
            const frameHeight = 808;
            const columns = 4;
            const rows = 3;
            const frames = [];

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < columns; col++) {
                    const frameIndex = row * columns + col;
                    if (frameIndex < 11) { // Process valid frames only
                        frames.push(
                            new Texture(
                                texture.source,
                                new Rectangle(
                                    col * frameWidth, // X position
                                    row * frameHeight, // Y position
                                    frameWidth, // Frame width
                                    frameHeight // Frame height
                                )
                            )
                        );
                    }
                }
            }

            // Create a sprite using the first (neutral) frame
            const sprite = new Sprite(frames[0]);
            sprite.anchor.set(0.5);
            sprite.x = app.screen.width / .5 ;
            sprite.y = app.screen.height / .666;

            // Add the sprite to the stage
            app.stage.addChild(sprite);

            // Define phoneme mappings to frames
            const phonemeMap = {
                neutral: 0,
                "A-I": 1,
                O: 2,
                U: 3,
                E: 4,
                F: 5,
                L: 6,
                "B-M-P": 7,
                "Q-W": 8,
                "CH-J-SH": 9,
                TH: 10,
            };

            // Function to update the sprite texture based on the phoneme
            function updateMouth(phoneme) {
                const frameIndex = phonemeMap[phoneme];
                if (frameIndex !== undefined) {
                    sprite.texture = frames[frameIndex];
                } else {
                    console.error(`Phoneme "${phoneme}" not found.`);
                }
            }

            // Example: Cycle through phonemes
            let frameIndex = 0;
            const interval = setInterval(() => {
                const phoneme = Object.keys(phonemeMap)[frameIndex % Object.keys(phonemeMap).length];
                updateMouth(phoneme);
                frameIndex++;
            }, 500);

            // Cleanup on component unmount
            return () => {
                clearInterval(interval);
            };
        })();

      }
    // Cleanup on component unmount
    return () => {
        if (appRef.current) {
            appRef.current.destroy(true, { children: true });
            appRef.current = null;
        }
    };
}, []);

return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
};

export default ThreeJSContainer;