# Accordion Components Documentation

This document provides an overview of the `Accordion`, `AccordionItem`, `AccordionTrigger`, and `AccordionContent` components exported from `frontend/src/components/ui/accordion.tsx`. These components are built on top of `@radix-ui/react-accordion` and provide a styled, collapsible content interface.

**General Purpose**: To offer accessible and customizable accordion functionality, allowing users to show and hide sections of content.

---

## `<Accordion />`

*   **Purpose**: This component serves as the root container for the entire accordion. It wraps one or more `AccordionItem` components.
*   **Underlying Component**: It is a direct export of `AccordionPrimitive.Root` from `@radix-ui/react-accordion`.
*   **Key Props**:
    *   `type: "single" | "multiple"`:
        *   Determines the behavior of the accordion.
        *   `"single"` (default): Allows only one item to be open at a time. Opening a new item will close the previously open one.
        *   `"multiple"`: Allows multiple items to be open simultaneously.
    *   `collapsible: boolean` (Only for `type="single"`):
        *   If `true`, allows the currently open item to be closed by clicking its trigger again.
    *   `defaultValue: string | string[]`: The value(s) of the item(s) that should be open by default. Use a string for `type="single"` or an array of strings for `type="multiple"`.
    *   `value: string | string[]`: Controlled value(s) of the open item(s).
    *   `onValueChange: (value: string | string[]) => void`: Callback function invoked when the open item(s) change.
    *   `className: string`: Standard React prop to apply custom CSS classes to the root element.
    *   Other props are forwarded to the underlying `AccordionPrimitive.Root` component.
*   **Usage**:
    ```tsx
    <Accordion type="single" collapsible className="w-full">
      {/* AccordionItem components go here */}
    </Accordion>
    ```
*   **Styling**: Does not apply specific styles itself but acts as a container. Styling is primarily applied to `AccordionItem`, `AccordionTrigger`, and `AccordionContent`.

---

## `<AccordionItem />`

*   **Purpose**: Represents an individual collapsible section within the `Accordion`. Each `AccordionItem` consists of an `AccordionTrigger` (the header) and an `AccordionContent` (the collapsible panel).
*   **Underlying Component**: A `React.forwardRef` component that wraps `AccordionPrimitive.Item`.
*   **Key Props**:
    *   `value: string` (Required): A unique value that identifies this item within the accordion. This value is used to control its open/closed state.
    *   `disabled: boolean`: If `true`, this item cannot be interacted with.
    *   `className: string`: Custom CSS classes to apply to the item.
    *   Other props are forwarded to the `AccordionPrimitive.Item`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `AccordionPrimitive.Item` element.
*   **Styling**:
    *   Applies `border-b border-white/20` using `cn` utility, creating a bottom border for separation. Additional classes can be passed via `className`.
*   **Usage**:
    ```tsx
    <AccordionItem value="item-1">
      <AccordionTrigger>Section 1 Title</AccordionTrigger>
      <AccordionContent>Section 1 content...</AccordionContent>
    </AccordionItem>
    ```

---

## `<AccordionTrigger />`

*   **Purpose**: The clickable header part of an `AccordionItem`. Clicking this trigger toggles the open/closed state of its corresponding `AccordionContent`.
*   **Underlying Component**: A `React.forwardRef` component that wraps `AccordionPrimitive.Trigger`, which is itself nested inside an `AccordionPrimitive.Header` (an `<h3>` element by default from Radix).
*   **Key Props**:
    *   `className: string`: Custom CSS classes to apply to the trigger button.
    *   `children: React.ReactNode`: The content of the trigger, typically text for the header.
    *   Other props are forwarded to the `AccordionPrimitive.Trigger`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `AccordionPrimitive.Trigger` (button) element.
*   **Styling**:
    *   Uses `cn` to apply several Tailwind CSS classes:
        *   `flex flex-1 items-center justify-between`: For layout of the trigger content and the chevron icon.
        *   `py-4 px-6`: Padding.
        *   `font-medium text-white`: Text styling.
        *   `transition-all hover:bg-white/5`: Hover effect.
        *   `[&[data-state=open]>svg]:rotate-180`: Rotates the chevron icon when the item is open.
        *   `rounded-lg`: Applies rounded corners.
    *   Includes a `ChevronDown` icon from `lucide-react` which has `h-4 w-4 shrink-0 transition-transform duration-200` classes for styling and animation.
*   **Structure**: The `AccordionPrimitive.Trigger` is wrapped within an `AccordionPrimitive.Header` (which is an `<h3>` by default) to ensure proper heading semantics for accessibility.
*   **Usage**:
    ```tsx
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    ```

---

## `<AccordionContent />`

*   **Purpose**: The collapsible panel of an `AccordionItem` that contains the content to be shown or hidden.
*   **Underlying Component**: A `React.forwardRef` component that wraps `AccordionPrimitive.Content`.
*   **Key Props**:
    *   `className: string`: Custom CSS classes to apply to the inner `div` that wraps the children.
    *   `children: React.ReactNode`: The content to be displayed within the collapsible panel.
    *   Other props are forwarded to the `AccordionPrimitive.Content`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `AccordionPrimitive.Content` element.
*   **Styling**:
    *   The `AccordionPrimitive.Content` element itself has classes:
        *   `overflow-hidden`: To ensure content is clipped during animation.
        *   `text-sm`: Default text size for content.
        *   `transition-all`: Smooth transition for properties.
        *   `data-[state=closed]:animate-accordion-up`: Applies a custom animation `accordion-up` when closing.
        *   `data-[state=open]:animate-accordion-down`: Applies a custom animation `accordion-down` when opening. (These animations would be defined in `tailwind.config.js` or global CSS).
    *   An inner `div` wraps the `children` and has `pb-4 pt-0 px-6` classes for padding, to which the `className` prop is also applied.
*   **Usage**:
    ```tsx
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
    ```

---

### Combined Usage Example:

```tsx
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion"; // Adjust path as needed

function MyAccordion() {
  return (
    <Accordion type="single" collapsible className="w-full">
      <AccordionItem value="item-1">
        <AccordionTrigger>What is the AI Lie Detector?</AccordionTrigger>
        <AccordionContent>
          The AI Lie Detector is a tool designed to analyze various communication cues...
        </AccordionContent>
      </AccordionItem>
      <AccordionItem value="item-2">
        <AccordionTrigger>How does it work?</AccordionTrigger>
        <AccordionContent>
          It uses advanced AI models to process audio and text, looking for patterns...
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
```

This structure creates a common accordion interface where each section can be expanded or collapsed by clicking its trigger. The `Accordion` component manages the overall state and behavior (single or multiple open items).
