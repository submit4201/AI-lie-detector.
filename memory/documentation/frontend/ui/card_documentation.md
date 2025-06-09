# Card Components Documentation

This document provides an overview of the Card components exported from `frontend/src/components/ui/card.tsx`. These components are used to group related content and actions into a container with a distinct visual style. They are built using `div` elements and styled with Tailwind CSS via the `cn` utility.

**General Purpose**: To provide a flexible and consistent way to display content in a card format, typically used for dashboards, item displays, or sectioned information.

---

## `<Card />`

*   **Purpose**: The main container for a card. It acts as a wrapper for all other card elements like `CardHeader`, `CardContent`, and `CardFooter`.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Allows for additional custom CSS classes to be applied to the card's root `div`.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `bg-card text-card-foreground`: Sets background and foreground colors (likely defined in `tailwind.config.js`).
        *   `flex flex-col gap-6`: Arranges children in a column with a gap of 6 units.
        *   `rounded-xl`: Applies large rounded corners.
        *   `border`: Adds a default border.
        *   `py-6`: Vertical padding of 6 units.
        *   `shadow-sm`: Applies a small box shadow.
    *   Includes a `data-slot="card"` attribute for potential global styling or selection.
*   **Usage**:
    ```tsx
    <Card className="w-full max-w-md">
      <CardHeader>...</CardHeader>
      <CardContent>...</CardContent>
      <CardFooter>...</CardFooter>
    </Card>
    ```

---

## `<CardHeader />`

*   **Purpose**: The header section of a card. Typically contains `CardTitle`, `CardDescription`, and optionally `CardAction`.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes for the header `div`.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `@container/card-header`: Defines a container query context named `card-header`.
        *   `grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5`: Sets up a grid layout optimized for a title and description, with items aligned to the start and a small gap.
        *   `px-6`: Horizontal padding.
        *   `has-data-[slot=card-action]:grid-cols-[1fr_auto]`: If a child element has `data-slot="card-action"`, the grid changes to two columns, allowing the action to be placed to the right of the title/description.
        *   `[.border-b]:pb-6`: If this `CardHeader` is followed by an element with a bottom border (likely a sibling, though the selector is a bit unusual and might be intended for a child or a specific scenario), it adds bottom padding.
    *   Includes a `data-slot="card-header"` attribute.
*   **Usage**:
    ```tsx
    <CardHeader>
      <CardTitle>Report Title</CardTitle>
      <CardDescription>A brief description of the report.</CardDescription>
      {/* Optional CardAction can go here */}
    </CardHeader>
    ```

---

## `<CardTitle />`

*   **Purpose**: Displays the title within a `CardHeader`.
*   **Underlying HTML Element**: `div` (Consider using `<h2>`, `<h3>`, etc., for semantic HTML, possibly by passing an `as` prop if the component were more complex, or by wrapping this in a heading tag).
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `leading-none font-semibold`: Sets line height to none and font weight to semi-bold.
    *   Includes a `data-slot="card-title"` attribute.
*   **Usage**:
    ```tsx
    <CardTitle>My Card Title</CardTitle>
    ```

---

## `<CardDescription />`

*   **Purpose**: Displays a description or subtitle text, typically within a `CardHeader` below the `CardTitle`.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `text-muted-foreground text-sm`: Sets text color to a muted foreground color and text size to small.
    *   Includes a `data-slot="card-description"` attribute.
*   **Usage**:
    ```tsx
    <CardDescription>This is a description for the card.</CardDescription>
    ```

---

## `<CardAction />`

*   **Purpose**: A container for action elements (e.g., a button or dropdown menu) typically placed within the `CardHeader`, aligned to the right.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `col-start-2 row-span-2 row-start-1 self-start justify-self-end`: These classes position the action element within the `CardHeader`'s grid when the `has-data-[slot=card-action]` condition is met on the `CardHeader`. It places the action in the second column, spanning two rows (if applicable), starting at the first row, aligning itself to the start of its grid area, and justifying itself to the end of its grid area (effectively right-aligning).
    *   Includes a `data-slot="card-action"` attribute, which is used by `CardHeader` for conditional styling.
*   **Usage**:
    ```tsx
    <CardHeader>
      <div>
        <CardTitle>Item Name</CardTitle>
        <CardDescription>Details about the item.</CardDescription>
      </div>
      <CardAction>
        {/* Button or Menu component */}
      </CardAction>
    </CardHeader>
    ```

---

## `<CardContent />`

*   **Purpose**: The main content area of the card, typically placed after `CardHeader` and before `CardFooter`.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `px-6`: Horizontal padding.
    *   Includes a `data-slot="card-content"` attribute.
*   **Usage**:
    ```tsx
    <CardContent>
      <p>This is the primary content of the card.</p>
    </CardContent>
    ```

---

## `<CardFooter />`

*   **Purpose**: The footer section of a card. Often used for action buttons (like "Save", "Cancel") or summary information.
*   **Underlying HTML Element**: `div`
*   **Key Props**:
    *   `className: string` (Optional): Custom CSS classes.
    *   `...props`: Accepts any standard HTML `div` attributes.
*   **Styling**:
    *   Uses `cn` to apply base Tailwind CSS classes:
        *   `flex items-center`: Arranges children in a row with items vertically centered.
        *   `px-6`: Horizontal padding.
        *   `[.border-t]:pt-6`: If this `CardFooter` is preceded by an element with a top border (likely a sibling, though the selector is a bit unusual), it adds top padding.
    *   Includes a `data-slot="card-footer"` attribute.
*   **Usage**:
    ```tsx
    <CardFooter>
      <Button variant="secondary">Cancel</Button>
      <Button>Save</Button>
    </CardFooter>
    ```

---

### Combined Usage Example:

```tsx
import {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
  CardAction // Assuming Button is imported from elsewhere
} from "@/components/ui/card";
import { Button } from "@/components/ui/button"; // Example import

function MyCustomCard() {
  return (
    <Card>
      <CardHeader>
        <div className="flex-grow">
          <CardTitle>Complex Analysis Report</CardTitle>
          <CardDescription>Results from the latest session.</CardDescription>
        </div>
        <CardAction>
          <Button variant="ghost" size="icon"> {/* More options icon */}
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        <p>Detailed findings and observations are presented here. This section can contain various elements like text, charts, or lists.</p>
      </CardContent>
      <CardFooter>
        <Button variant="outline">View Details</Button>
        <Button>Process Again</Button>
      </CardFooter>
    </Card>
  );
}
```
