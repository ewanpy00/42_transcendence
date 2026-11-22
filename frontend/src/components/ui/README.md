
# ft_transcendence — UI Kit

Reusable React + TypeScript UI components for the
ft_transcendence frontend.

## Components

| Component | Purpose |
|-----------|---------|
| Button | Primary, secondary, and danger actions |
| Input | Labeled text and form inputs |
| Select | Labeled dropdown selections |
| Spinner | Loading indicators |
| Avatar | User image or initials fallback |
| Modal | Accessible popup dialogs |
| Toast | Success, error, and info notifications |

## Usage

Import components directly from the UI folder.

### Button

```tsx
import { Button } from "./components/ui/Button";

<Button onClick={() => alert("Clicked!")}>
  Find Partner
</Button>

<Button variant="secondary">Cancel</Button>
<Button variant="danger">Leave Chat</Button>
<Button disabled>Send Message</Button>
```

Variants: `primary` (default), `secondary`, `danger`.

### Input

```tsx
import { Input } from "./components/ui/Input";

<Input
  id="username"
  label="Username"
  placeholder="Enter your username"
/>
```

`id` and `label` are required. Standard HTML input
attributes are supported.

### Select

```tsx
import { Select } from "./components/ui/Select";

<Select
  id="language"
  label="Language"
  options={[
    { value: "en", label: "English" },
    { value: "ar", label: "Arabic" }
  ]}
/>
```

`id`, `label`, and `options` are required.

### Spinner

```tsx
import { Spinner } from "./components/ui/Spinner";

<Spinner label="Finding a partner" />
```

The label provides an accessible loading description.

### Avatar

```tsx
import { Avatar } from "./components/ui/Avatar";

<Avatar name="Aisha Mohammed" />
<Avatar name="Aisha Mohammed" src="/avatar.png" />
```

If the image is missing or fails to load, the
component displays initials.

### Modal

```tsx
import { useState } from "react";
import { Button } from "./components/ui/Button";
import { Modal } from "./components/ui/Modal";

function Example() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        Open Modal
      </Button>

      <Modal
        isOpen={open}
        onClose={() => setOpen(false)}
        title="Leave Chat?"
      >
        <p>Are you sure?</p>
      </Modal>
    </>
  );
}
```

The Modal uses the native HTML dialog element.
It supports Escape to close and keyboard navigation.

### Toast

```tsx
import { useState } from "react";
import { Button } from "./components/ui/Button";
import { Toast } from "./components/ui/Toast";

function Example() {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <Button onClick={() => setVisible(true)}>
        Show Notification
      </Button>

      {visible && (
        <Toast
          message="Partner found!"
          variant="success"
          onClose={() => setVisible(false)}
        />
      )}
    </>
  );
}
```

Variants: `success`, `error`, `info`.

Toast dismissal is controlled by the parent.
Automatic dismissal is not implemented.

## Design tokens

Shared CSS variables are defined in:

`frontend/src/styles/tokens.css`

The application's entry point should import the
tokens once:

```tsx
import "./styles/tokens.css";
```

Import this from `frontend/src/main.tsx` when the
main frontend setup is ready.

Individual components use their own CSS files.

## Validation

The components were tested in a separate Vite
React + TypeScript playground while the main
frontend setup was being prepared.

- Production build: passed
- Lint: passed
- Basic browser interactions: passed
- Mobile viewport at 375px: reviewed
- Modal keyboard navigation: passed

Full integration with the main application remains
to be verified.
