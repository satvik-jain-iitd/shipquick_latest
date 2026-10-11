# Design Tokens for shipquick_latest

> Generalized from Material 3 Design System and Legacy DLS

## Color Palette

| Token | Material 3 Default | Description | Your Value |
|---|---|---|---|
| `<PRIMARY_COLOR>` | `#3B82F6` | Primary brand color | `#XXXXXX` |
| `<PRIMARY_DARK>` | `#2563EB` | Primary dark variant | `#XXXXXX` |
| `<TEXT_COLOR>` | `#1F2937` | Primary text color | `#XXXXXX` |
| `<BG_COLOR>` | `#FFFFFF` | Main background | `#XXXXXX` |
| `<TEXT_SECONDARY>` | `#6B7280` | Secondary text color | `#XXXXXX` |
| `<BG_ALT>` | `#F3F4F6` | Alternative background | `#XXXXXX` |

## Typography

| Token | Material 3 Default | Description | Your Value |
|---|---|---|---|
| `<PRIMARY_FONT>` | `Roboto` | Interface font family | `Arial` / `Helvetica` / `Your Font` |
| `<FONT_SIZE_BASE>` | `16px` | Base font size | `14px` / `16px` |
| `<FONT_SIZE_HEADING>` | `24px` | Heading font size | `20px` / `24px` / `32px` |

## Spacing System

| Token | Material 3 Default | Description | Your Value |
|---|---|---|---|
| `<SPACING_UNIT>` | `4px` | Base spacing increment | `4px` / `8px` / `16px` |
| `<SPACING_1>` | `4px` | 0.5x unit | `2px` / `4px` / `8px` |
| `<SPACING_2>` | `8px` | 1x unit | `4px` / `8px` / `16px` |
| `<SPACING_3>` | `16px` | 2x unit | `8px` / `16px` / `32px` |
| `<SPACING_4>` | `24px` | 3x unit | `12px` / `24px` / `48px` |

## Motion (if applicable)

| Token | Material 3 Default | Description | Your Value |
|---|---|---|---|
| `<TRANSITION_DURATION>` | `0.2s` | Default transition time | `0.1s` / `0.2s` / `0.3s` |
| `<EASING_FUNCTION>` | `ease` | Default easing | `ease` / `ease-in` / `ease-out` / `cubic-bezier(...)` |

## How to Use Design Tokens

1. **Replace placeholder values** in this file with your project's actual brand assets
2. **Reference tokens** in your CSS/design system using the token names
3. **Consistency**: All UI elements should use the defined tokens, not hardcoded values
4. **Expand**: Add more tokens as needed for your project (colors, shadows, etc.)

## Example Usage

```css
/* Using design tokens in your CSS */
.button-primary {
  background-color: var(--<PRIMARY_COLOR>);
  color: var(--<TEXT_COLOR>);
  padding: var(--<SPACING_2>);
  font-family: var(--<PRIMARY_FONT>);
  font-size: var(--<FONT_SIZE_BASE>");
}

.heading-primary {
  color: var(--<PRIMARY_COLOR>);
  font-size: var(--<FONT_SIZE_HEADING>);
  margin-bottom: var(--<SPACING_3>);
}
```

---

**Replace all `<PLACEHOLDER>` values** with your project-specific assets before starting development.

**Inspired by**: Legacy design system and Google Material Design 3 design tokens.