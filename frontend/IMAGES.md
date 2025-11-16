# Image Setup Instructions

## Interactive Slider Images

The interactive slider component requires two images. Currently, placeholder SVG images are being used.

To replace them with actual images:

1. Add your images to the `public/images/` directory (e.g., `image1.jpg` and `image2.jpg`)
2. Update the image paths in `app/page.tsx`:

```typescript
const image1 = "/images/image1.jpg";
const image2 = "/images/image2.jpg";
```

The slider will:
- Initially display image 1 (100%)
- When the cursor moves left of center, show more of image 2
- When the cursor moves right of center, show more of image 1
- The white bar follows the cursor's X position

