# Canvas Flowchart Generation Template

## Standard Layout Coordinates

### Main Flow (Center Line)
- Center X: 350
- Node width: 300
- Vertical spacing: 150px

```
Input Node:        y=0
Classification:     y=170 (gap 170)
Path Computation:   y=380 (gap 210, larger node)
File Generation:    y=580 (gap 200)
Output:             y=920 (gap 340, includes sub-nodes)
```

### File Generation Section (Group)
- Group bounds: x=100 to 900, y=550 to 870
- Note node: x=130, y=590
- Meta node: x=130, y=730
- Canvas node: x=400, y=590
- Base node: x=670, y=590
- Routing node: x=400, y=730

### Color Scheme
- Input: color 6 (purple)
- Processing: color 3 (yellow)
- Critical: color 1 (red)
- Required output: color 4 (green)
- Optional output: color 2 (orange) or 3 (yellow)
- Final output: color 5 (cyan)

## Standard Node IDs

Always use these IDs for consistency:
- node-input
- node-classify
- node-paths
- node-note
- node-meta
- node-canvas
- node-base
- node-routing
- node-output
- group-generation

## Edge Connection Pattern

Vertical flow:
```
node-input → node-classify → node-paths → node-routing
node-routing → node-note
node-routing → node-canvas (conditional)
node-routing → node-base (conditional)
node-note → node-meta
node-meta → node-output
node-base → node-output
```

## Text Template

```markdown
## [Title]

[Content with bold for key terms]

- Bullet point 1
- Bullet point 2
```

## Reproducibility Checklist

- [ ] Use fixed X coordinates (not calculated)
- [ ] Use consistent node IDs
- [ ] Use consistent color codes
- [ ] Use standard spacing (150-200px)
- [ ] Center main flow at X=350
- [ ] Side branches at X=130, 400, 670
