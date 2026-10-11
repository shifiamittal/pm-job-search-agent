# Resume Template Usage Guide

## Principle

> Manifest = content source  
> Template = formatting source

The template must never become a hidden content source.

## May be reused from template
- margins
- font family / size
- heading style
- bullet indentation
- spacing
- tab stops
- columns
- header layout
- hyperlink formatting
- date / location alignment
- section hierarchy

## May not be reused unless present in manifest
- old summary
- old bullets
- old competencies
- old metrics
- old headline
- old target-role wording
- old company-specific wording

## Safe process
1. Parse template.
2. Capture styles / formatting.
3. Remove or replace old content.
4. Insert manifest content exactly.
5. Preserve formatting only.
6. Save as new file.
7. Extract generated text.
8. Compare to manifest.
9. Check for old-template leakage.
10. Only after exact-content validation, render and inspect layout.

## Leakage audit
Flag:
- any old sentence not in manifest
- any extra bullet
- any old metric
- any outdated role / company reference

Leakage is a hard failure.

## Page-fit rule
If exact manifest produces too many pages:
1. keep exact document
2. render
3. measure page pressure
4. return to Writing
5. revise approved content
6. create new manifest
7. regenerate
8. revalidate
