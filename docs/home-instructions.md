# Directive: Implement Cheerful Theme for shadcn/ui

This directive outlines the necessary code changes to configure a shadcn/ui project with a cheerful, warm, rounded aesthetic (based on the "Nanobanana Pro" reference).

---

## Prerequisites: Fonts

Ensure the **Nunito** font is loaded in your project's entry point (e.g., `index.html` for Vite, or `app/layout.tsx` for Next.js with `next/font`).

**Example HTML import:**

```html
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
```

---

## Step 1: Update Global Stylesheets

Replace the contents of your main global CSS file (e.g., `app/globals.css` or `src/index.css`) with the following code. This defines the cheerful color palette using HSL variables and increases the default border radius.

**File: `app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
 
@layer base {
  :root {
    /* Theme: Cheerful Banana 
      Aesthetic: Warm, sunny, soft, bubbly.
    */

    /* Background: A very soft, creamy off-white */
    --background: 45 100% 99%; 
    /* Foreground: A warm, deep brownish-gray instead of harsh black */
    --foreground: 30 10% 20%;

    /* Card: Pure white to pop against the creamy background */
    --card: 0 0% 100%;
    --card-foreground: 30 10% 20%;
 
    /* Popover: Same as card */
    --popover: 0 0% 100%;
    --popover-foreground: 30 10% 20%;
 
    /* Primary: The sunny "banana" yellow/gold */
    --primary: 47 100% 50%;
    /* Primary text: Dark brown for contrast on the yellow */
    --primary-foreground: 30 20% 15%;
 
    /* Secondary: A soft, pale yellow for lighter buttons */
    --secondary: 50 100% 91%;
    --secondary-foreground: 30 20% 15%;
 
    /* Muted: Very subtle warm backgrounds (like input interiors) */
    --muted: 45 100% 96%;
    --muted-foreground: 30 10% 50%; /* Softer text for placeholders */
 
    /* Accent: Used for hover states. A very pale sky blue for nice contrast */
    --accent: 200 90% 94%;
    --accent-foreground: 30 10% 20%;
 
    /* Destructive: A slightly warmer red */
    --destructive: 0 85% 60%;
    --destructive-foreground: 0 0% 98%;

    /* Border/Input: Soft warm pale yellow/gray for outlines */
    --border: 50 60% 90%;
    --input: 50 60% 90%;
    /* Ring: Matches primary yellow for focus states */
    --ring: 47 100% 50%;
 
    /* Radius: Increased heavily for the "bubbly" look. Default is often 0.5rem */
    --radius: 1.25rem;
  }
 
  .dark {
    /* Cheerful Dark Mode
       Aesthetic: Deep warm charcoal background with bright yellow pops.
    */
    --background: 30 15% 10%; /* Deep warm charcoal */
    --foreground: 45 20% 90%; /* Warm light cream text */
 
    --card: 30 15% 12%;
    --card-foreground: 45 20% 90%;
 
    --popover: 30 15% 12%;
    --popover-foreground: 45 20% 90%;
 
    /* Keep primary bright yellow for pop */
    --primary: 47 100% 50%;
    --primary-foreground: 30 20% 15%;
 
    --secondary: 30 15% 20%;
    --secondary-foreground: 45 20% 90%;
 
    --muted: 30 15% 15%;
    --muted-foreground: 30 10% 60%;
 
    --accent: 30 15% 25%;
    --accent-foreground: 45 20% 90%;
 
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 45 20% 90%;
 
    --border: 30 15% 20%;
    --input: 30 15% 20%;
    --ring: 47 100% 50%;
  }
}
 
@layer base {
  * {
    @apply border-border;
  }
  body {
    /* Applying the background and font, and adding a subtle texture */
    @apply bg-background text-foreground font-sans antialiased;
    /* Optional: Adds a subtle warm grain texture to the background for depth */
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  }
  /* Ensure headings use the heaviest font weights for the bubbly look
  */
  h1, h2, h3, h4, h5, h6 {
    @apply font-extrabold tracking-tight;
  }
}
```

---

## Step 2: Update Tailwind Configuration

Update your Tailwind configuration to map the new CSS variables to Tailwind utilities and set Nunito as the default sans-serif font.

**File: `tailwind.config.js` (or `.ts`)**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
	],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        // Set Nunito as the default sans font for that friendly look
        // Ensure "Nunito" is loaded in your project fonts
        sans: ["Nunito", "sans-serif"],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        // Add a subtle bounce animation for hover states
        "bounce-slow": {
            '0%, 100%': { transform: 'translateY(-5%)', animationTimingFunction: 'cubic-bezier(0.8, 0, 1, 1)' },
            '50%': { transform: 'translateY(0)', animationTimingFunction: 'cubic-bezier(0, 0, 0.2, 1)' },
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "bounce-slow": "bounce-slow 3s infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

---

## Step 3: Implementation Example (Verification)

The following React component demonstrates how standard shadcn/ui components will automatically inherit the new cheerful theme.

**File: `components/ThemeTestExample.tsx`**

```jsx
import React from 'react';
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"

export default function ThemeTestExample() {
  return (
    <div className="p-10 bg-background min-h-screen flex justify-center items-center">
      <Card className="w-[500px] shadow-xl shadow-primary/10 border-2">
        <CardHeader>
            <CardTitle className="text-2xl">Let's Learn!</CardTitle>
            <CardDescription>Standard shadcn components with a cheerful twist.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
           <div className="space-y-2">
              <label className="font-bold ml-1">Give it a name!</label>
              {/* The Input will automatically be bubbly with a warm border and ring */}
              <Input 
                placeholder="e.g., Song Lyrics 🎵" 
                className="bg-muted/30 border-2 focus-visible:ring-primary h-12 text-lg font-semibold" 
              />
           </div>

           <div className="space-y-2">
             <label className="font-bold ml-1">Content</label>
             <Textarea 
               placeholder="Paste text here..." 
               // Using bg-muted gives it a soft cream "notebook" look
               className="min-h-[150px] bg-muted/50 border-2 focus-visible:ring-primary resize-none text-base shadow-inner" 
             />
           </div>

           {/* The Button will be bright yellow, rounded, and bold automatically */}
           <Button size="lg" className="w-full font-extrabold text-lg shadow-md shadow-primary/30 hover:-translate-y-1 transition-all">
             Create Magic Flashcards! ✨
           </Button>
           
           <div className="flex justify-center">
              <Button variant="ghost" className="text-muted-foreground hover:bg-secondary hover:text-secondary-foreground">
                 Skip for now
              </Button>
           </div>
        </CardContent>
      </Card>
    </div>
  );
}
```