import { staticFile, continueRender, delayRender } from "remotion";

export const FONT_FAMILY = "Source Han Sans TW";

const waitForFont = delayRender("Loading Source Han Sans TW");

const regular = new FontFace(FONT_FAMILY, `url(${staticFile("SourceHanSansTW-Regular.otf")})`, {
  weight: "400",
});
const bold = new FontFace(FONT_FAMILY, `url(${staticFile("SourceHanSansTW-Bold.otf")})`, {
  weight: "700",
});

Promise.all([regular.load(), bold.load()])
  .then(([loadedRegular, loadedBold]) => {
    document.fonts.add(loadedRegular);
    document.fonts.add(loadedBold);
    continueRender(waitForFont);
  })
  .catch((err) => {
    console.log("Source Han Sans failed to load", err);
    continueRender(waitForFont);
  });
