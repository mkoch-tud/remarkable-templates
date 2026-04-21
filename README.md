# Remarkable Templates

Custom templates for reMarkable.
All of them continue creating new lines when scrolling.


> 🤖 **AI Notice:** These templates were partly created with the help of Claude Opus 4.6 to initially understand the JSON syntax for building these templates.

## Available templates

Currently included in this repository:

- `Daily-Planner`
- `Daily-ToDo`
- `Meeting-Minutes`
- `Outline-Method`
- `Quadrant-Method`

## Setup

1. Connect to your reMarkable over SSH.
2. Copy your selected template file to:
	 - `/usr/share/remarkable/templates`
3. Open `/usr/share/remarkable/templates/templates.json` and register the template by adding a new object at the end of the registered template list.

Use one entry like this (placeholders shown first, current values shown as an example):

```json
{
	"name": "<TEMPLATE_DISPLAY_NAME>",
	"filename": "<TEMPLATE_FILENAME_WITHOUT_EXTENSION>",
	"iconCode": "<ICON_CODE>",
	"categories": ["<CATEGORY>"]
}
```

Example values based on this repo:

- `<TEMPLATE_DISPLAY_NAME>` -> `Outline Method`
- `<TEMPLATE_FILENAME_WITHOUT_EXTENSION>` -> `Outline-Method`
- `<ICON_CODE>` -> `\ue98c`
- `<CATEGORY>` -> `Custom`

4. Save the file, close it, and then restart the UI:

```bash
systemctl restart xochitl
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for the full text.

Provided "as is", without warranty of any kind.
