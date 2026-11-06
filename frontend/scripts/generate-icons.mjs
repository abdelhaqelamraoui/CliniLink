// Builds the app icons from public/logo-mark.svg:
//   app/icon.svg        modern browsers (scalable)
//   app/favicon.ico     16/32/48 px, for older browsers and bookmarks
//   app/apple-icon.png  180 px, full-bleed square (iOS rounds the corners itself)
// Run: npm run icons
import { readFile, writeFile, copyFile } from "node:fs/promises";
import sharp from "sharp";

const svg = await readFile("public/logo-mark.svg", "utf8");
await copyFile("public/logo-mark.svg", "app/icon.svg");

const png = (source, size) => sharp(Buffer.from(source)).resize(size, size).png().toBuffer();

// ICO container holding PNG images (supported by every current browser).
const sizes = [16, 32, 48];
const images = await Promise.all(sizes.map((s) => png(svg, s)));
const header = Buffer.alloc(6 + 16 * sizes.length);
header.writeUInt16LE(0, 0);
header.writeUInt16LE(1, 2);
header.writeUInt16LE(sizes.length, 4);
let offset = header.length;
sizes.forEach((size, i) => {
  const e = 6 + 16 * i;
  header.writeUInt8(size, e);
  header.writeUInt8(size, e + 1);
  header.writeUInt16LE(1, e + 4);
  header.writeUInt16LE(32, e + 6);
  header.writeUInt32LE(images[i].length, e + 8);
  header.writeUInt32LE(offset, e + 12);
  offset += images[i].length;
});
await writeFile("app/favicon.ico", Buffer.concat([header, ...images]));

const square = svg.replace('rx="13"', 'rx="0"');
await writeFile("app/apple-icon.png", await png(square, 180));
console.log("Icons written: app/icon.svg, app/favicon.ico, app/apple-icon.png");
