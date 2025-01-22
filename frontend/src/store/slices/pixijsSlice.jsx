import { createSlice } from "@reduxjs/toolkit";

const pixijsSlice = createSlice({
    name: 'pixijs',
    initialState: {
        isTalking: false,
        visemes: [],
        visemesIndex: 0,
        visemesStartTime: 0,
        baseDimensions: { width: 648, height: 900 },
    },
    reducers: {
        setIsTalking: (state, action) => {
            state.isTalking = action.payload;
        },
        setVisemes: (state, action) => {
            state.visemes = action.payload;
        },
        setVisemesIndex: (state, action) => {
            state.visemesIndex = action.payload;
        },
        setVisemesStartTime: (state, action) => {
            state.visemesStartTime = action.payload;
        },
    },
});

export const { setIsTalking, setVisemes, setVisemesIndex, setVisemesStartTime } = pixijsSlice.actions;
export default pixijsSlice.reducer;