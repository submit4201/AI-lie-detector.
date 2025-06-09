# Tabs Components Documentation

This document provides an overview of the `Tabs`, `TabsList`, `TabsTrigger`, and `TabsContent` components exported from `frontend/src/components/ui/tabs.tsx`. These components are built upon `@radix-ui/react-tabs` and provide a styled, accessible, and interactive tabbed interface.

**General Purpose**: To allow users to navigate between different sections of content within the same page or component, where each section is displayed in a separate "tab panel."

---

## `<Tabs />`

*   **Purpose**: This component serves as the root container for the entire tabbed interface. It wraps the `TabsList` (containing tab buttons) and the associated `TabsContent` (tab panels).
*   **Underlying Component**: It is a direct export of `TabsPrimitive.Root` from `@radix-ui/react-tabs`.
*   **Key Props**:
    *   `defaultValue: string` (Optional): The `value` of the tab that should be active by default when the component mounts.
    *   `value: string` (Optional): Can be used to control the active tab from outside the component.
    *   `onValueChange: (value: string) => void` (Optional): Callback function invoked when the active tab changes.
    *   `orientation: "horizontal" | "vertical"` (Optional, default: `"horizontal"`): Determines the orientation of the tabs.
    *   `activationMode: "automatic" | "manual"` (Optional, default: `"automatic"`):
        *   `"automatic"`: Activating a tab is done by focusing it (e.g., via keyboard navigation).
        *   `"manual"`: Activating a tab requires an explicit click or Enter/Space key press.
    *   `className: string` (Optional): Standard React prop to apply custom CSS classes to the root `div` element of the tabs container.
    *   Other props are forwarded to the underlying `TabsPrimitive.Root` component.
*   **Usage**:
    ```tsx
    <Tabs defaultValue="account" className="w-[400px]">
      <TabsList>...</TabsList>
      <TabsContent value="account">...</TabsContent>
      <TabsContent value="password">...</TabsContent>
    </Tabs>
    ```
*   **Styling**: Does not apply specific styles itself but acts as the main container and state manager for the tab system.

---

## `<TabsList />`

*   **Purpose**: This component is a container for one or more `TabsTrigger` components. It visually groups the tab buttons.
*   **Underlying Component**: A `React.forwardRef` component that wraps `TabsPrimitive.List`.
*   **Key Props**:
    *   `loop: boolean` (Optional, default: `true`): When `true`, keyboard navigation will loop from the last tab to the first and vice-versa.
    *   `className: string` (Optional): Custom CSS classes to apply to the list container.
    *   Other props are forwarded to `TabsPrimitive.List`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `TabsPrimitive.List` element.
*   **Styling**:
    *   Uses `cn` to apply Tailwind CSS classes for a distinct appearance:
        *   `inline-flex h-12 items-center justify-center`: Basic flex layout for horizontal alignment, fixed height.
        *   `rounded-lg`: Rounded corners for the list container.
        *   `bg-white/10 backdrop-blur-md`: Semi-transparent white background with a backdrop blur effect.
        *   `border border-white/20`: Semi-transparent white border.
        *   `p-1`: Padding within the list.
        *   `text-slate-300`: Default text color for items within (though `TabsTrigger` overrides this).
        *   `shadow-lg`: Applies a large shadow.
*   **Usage**:
    ```tsx
    <TabsList>
      <TabsTrigger value="profile">Profile</TabsTrigger>
      <TabsTrigger value="settings">Settings</TabsTrigger>
    </TabsList>
    ```

---

## `<TabsTrigger />`

*   **Purpose**: Represents an individual tab button. Clicking a `TabsTrigger` activates its associated `TabsContent` panel.
*   **Underlying Component**: A `React.forwardRef` component that wraps `TabsPrimitive.Trigger`.
*   **Key Props**:
    *   `value: string` (Required): A unique value that associates this trigger with a specific `TabsContent` panel.
    *   `disabled: boolean` (Optional): If `true`, the tab trigger is not interactive.
    *   `className: string` (Optional): Custom CSS classes for the trigger button.
    *   `children: React.ReactNode`: The content of the tab button, typically text.
    *   Other props are forwarded to `TabsPrimitive.Trigger`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `TabsPrimitive.Trigger` (button) element.
*   **Styling**:
    *   Uses `cn` to apply a comprehensive set of Tailwind CSS classes for base style, hover effects, focus visibility, disabled state, and active state:
        *   Base: `inline-flex items-center justify-center whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium text-slate-300`
        *   Transitions: `transition-all duration-300`
        *   Focus: `ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2`
        *   Disabled: `disabled:pointer-events-none disabled:opacity-50`
        *   Hover (inactive): `hover:text-white hover:bg-white/10`
        *   Active (`data-[state=active]`):
            *   `bg-gradient-to-r from-purple-600/30 to-blue-600/30` (gradient background)
            *   `text-white` (active text color)
            *   `shadow-md`
            *   `backdrop-blur-sm`
            *   `border border-purple-400/50` (adds a border when active)
*   **Usage**:
    ```tsx
    <TabsTrigger value="tab1">Tab One</TabsTrigger>
    ```

---

## `<TabsContent />`

*   **Purpose**: The panel that displays the content for an active tab. Its visibility is controlled by the `Tabs` component based on the active `TabsTrigger`.
*   **Underlying Component**: A `React.forwardRef` component that wraps `TabsPrimitive.Content`.
*   **Key Props**:
    *   `value: string` (Required): The value that associates this content panel with a specific `TabsTrigger`. When the trigger with the matching value is active, this content is displayed.
    *   `forceMount: boolean` (Optional): If `true`, the content will be mounted in the DOM even when its tab is inactive. Useful for components that need to maintain state or for SEO purposes.
    *   `className: string` (Optional): Custom CSS classes for the content panel.
    *   `children: React.ReactNode`: The content to be displayed within the panel.
    *   Other props are forwarded to `TabsPrimitive.Content`.
*   **Ref Forwarding**: Forwards `ref` to the underlying `TabsPrimitive.Content` element.
*   **Styling**:
    *   Uses `cn` to apply Tailwind CSS classes:
        *   `mt-6`: Margin top to separate it from the `TabsList`.
        *   Focus visibility: `ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2`
        *   Animation: `animate-in fade-in-50 slide-in-from-bottom-1 duration-300`. (These animation classes like `animate-in`, `fade-in-50`, `slide-in-from-bottom-1` are likely custom animations defined in `tailwind.config.js` or global CSS, triggered by `data-[state=open]` or `data-[state=closed]` which Radix UI applies, though not explicitly shown in this component's classes).
*   **Usage**:
    ```tsx
    <TabsContent value="tab1">
      <p>Content for Tab One.</p>
    </TabsContent>
    ```

---

### Combined Usage Example:

```tsx
import {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
} from "@/components/ui/tabs"; // Adjust path as needed

function MyTabsComponent() {
  return (
    <Tabs defaultValue="profile" className="w-full">
      <TabsList>
        <TabsTrigger value="profile">Profile</TabsTrigger>
        <TabsTrigger value="account">Account</TabsTrigger>
        <TabsTrigger value="settings" disabled>Settings (Disabled)</TabsTrigger>
      </TabsList>
      <TabsContent value="profile">
        <p>This is the profile tab content.</p>
      </TabsContent>
      <TabsContent value="account">
        <p>This is the account tab content.</p>
      </TabsContent>
      <TabsContent value="settings">
        <p>This is the settings tab content (will not be initially visible or easily navigable if trigger is disabled).</p>
      </TabsContent>
    </Tabs>
  );
}
```
This example shows a basic tabbed interface with three tabs, one of which is disabled. The "profile" tab will be active by default. Clicking on "Account" will switch to its content.

---
