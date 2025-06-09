# Badge Component Documentation

This document provides an overview of the `Badge` component and the `badgeVariants` object exported from `frontend/src/components/ui/badge.jsx`. The `Badge` component is used for displaying small pieces of information, statuses, tags, or labels in a visually distinct manner.

---

## `badgeVariants` Object

*   **Purpose**: The `badgeVariants` object defines a collection of predefined visual styles for the `Badge` component. Each key in this object represents a `variant` name, and its value is a string of Tailwind CSS classes that define the appearance of that variant.
*   **Structure**: It's a plain JavaScript object where keys are variant names (strings) and values are strings of Tailwind CSS classes.
*   **Defined Variants and Styles**:
    *   `default`: Primary background, primary foreground text, hover effect.
        *   Classes: `bg-primary text-primary-foreground hover:bg-primary/80`
    *   `secondary`: Secondary background, secondary foreground text, hover effect.
        *   Classes: `bg-secondary text-secondary-foreground hover:bg-secondary/80`
    *   `destructive`: Destructive action background (typically red), destructive foreground text, hover effect.
        *   Classes: `bg-destructive text-destructive-foreground hover:bg-destructive/80`
    *   `outline`: Transparent background with a border, foreground text, hover effects for background and text.
        *   Classes: `text-foreground border border-input bg-background hover:bg-accent hover:text-accent-foreground`
    *   `success`: Green background, green text, hover effect (with dark mode variants).
        *   Classes: `bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-300`
    *   `warning`: Yellow background, yellow text, hover effect (with dark mode variants).
        *   Classes: `bg-yellow-100 text-yellow-800 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-300`
    *   `error`: Red background, red text, hover effect (with dark mode variants). (Similar to `destructive` but potentially with different shades or semantic meaning).
        *   Classes: `bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900 dark:text-red-300`
    *   `purple`: Purple background, purple text, hover effect (with dark mode variants).
        *   Classes: `bg-purple-100 text-purple-800 hover:bg-purple-200 dark:bg-purple-900 dark:text-purple-300`
    *   `blue`: Blue background, blue text, hover effect (with dark mode variants).
        *   Classes: `bg-blue-100 text-blue-800 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300`
    *   `gradient`: Gradient background (purple to blue), white text, hover effect on the gradient.
        *   Classes: `bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600`
*   **Usage**: The `Badge` component uses this object to look up the class string corresponding to the `variant` prop.

---

## `<Badge />` Component

*   **Purpose**: The `Badge` component is a React functional component used to render a small, styled inline element, typically for displaying status indicators, tags, categories, or short informational snippets.
*   **Underlying HTML Element**: Renders a `div` element.
*   **Key Props**:
    *   `variant: string` (Default: `"default"`):
        *   Determines the visual style of the badge. It should correspond to one of the keys defined in the `badgeVariants` object (e.g., "default", "secondary", "success", "gradient").
        *   If an invalid variant name is provided or if the variant is not found in `badgeVariants`, the base styling will still apply, but without specific variant colors.
    *   `className: string`:
        *   Allows for additional custom CSS classes to be applied to the badge, enabling further customization beyond the predefined variants.
    *   `...props`: Any other standard HTML attributes (e.g., `id`, `title`, event handlers like `onClick`) can be passed down to the underlying `div` element.
*   **Styling Mechanism**:
    *   Uses the `cn` utility function (which typically combines `clsx` for conditional class names and `tailwind-merge` for resolving conflicting Tailwind CSS classes).
    *   **Base Styles**: Always applies a set of base Tailwind CSS classes for common styling:
        *   `inline-flex items-center`: For proper alignment of content within the badge.
        *   `rounded-full`: Makes the badge pill-shaped.
        *   `border`: Applies a default border (its color might be overridden by variant or `className`).
        *   `px-2.5 py-0.5`: Horizontal and vertical padding.
        *   `text-xs font-semibold`: Small text size and semi-bold font weight.
        *   `transition-colors`: Smooth transition for color changes (e.g., on hover).
        *   `focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2`: Focus ring styling for accessibility.
    *   **Variant Styles**: Appends the class string from `badgeVariants[variant]` based on the `variant` prop.
    *   **Custom Styles**: Appends any classes passed via the `className` prop.
*   **Reliance on Utilities**:
    *   `cn` (from `@/lib/utils`): For constructing the final `className` string. This implies the use of `clsx` and `tailwind-merge` in the project's `utils`.
    *   While `class-variance-authority` (CVA) is not directly used in *this specific file* to define `badgeVariants`, the pattern of having a variants object and applying classes based on a `variant` prop is very similar to how CVA is used. The `cn` utility is often used in conjunction with CVA.

### Usage Examples

```jsx
import { Badge } from "@/components/ui/badge"; // Adjust path as needed

function MyComponent() {
  return (
    <div>
      <Badge>Default Badge</Badge>
      <Badge variant="secondary">Secondary Badge</Badge>
      <Badge variant="destructive">Destructive Badge</Badge>
      <Badge variant="outline">Outline Badge</Badge>
      <Badge variant="success" className="ml-2">Success!</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="purple">Purple Tag</Badge>
      <Badge variant="blue">Info</Badge>
      <Badge variant="gradient" title="This is a gradient badge">
        Gradient
      </Badge>
    </div>
  );
}
```

This demonstrates how to use the `Badge` component with different `variant` props to achieve various visual styles, and how to add custom classes or other HTML attributes.

---
