# Changelog

## [Unreleased]

## [v0.2.0] - 04/10/2026

* ⭐ `prespyc.to_python()`: script values as plain dicts and lists
* ⭐ `Script`: what an action block does, read off its bytecode
* ⭐ `FrameObject.clip_actions`: the `onClipEvent()` handlers of a placement
* ⭐ `FrameObject.place()`, `tag_matrix`, `with_placement()`: place by the PlaceObject matrix
* ⭐ `Timeline.pad_to()`, `repeat()`, `rotate()`, `hold()`, `keep_ranges()`, `sequence()`
* ⭐ `Substitute` modifier: swap characters by id through the tree
* ⭐ `Matrix @ Matrix`: composition
* ⭐ `ShapeBuilder`: draw a shape character from scratch
* ⭐ `RenderedFrames` and `Spritesheet.pages()`: pack a page at a time, in bounded memory
* ⭐ Draw buttons (up state) and static texts (`DefineText`)
* 🪲 Drop gradient stops whose ratio does not exceed the previous one
* 🪲 A sprite used as a mask lands where it draws, not off by its bounds
* 🪲 A nested clip plays from the frame placing it, and loops unless a script or its placement's load handler stops it
* 🪲 The canvas holds the room filters draw over, as FFdec's does: `Converter.canvas_bounds()`, `bounds=`
* 🪲 `ffdec_export(subframes=n)` plays the nested clips of the frame, as `-sublength` does, instead of repeating it
* 🪲 An empty drawable renders as a blank image instead of failing in the rasterizer
* 🪲 `subpixel_stroke_width=False` floors strokes at one output pixel, through the zoom and the placements, instead of relying on the `vector-effect` resvg ignores


## [v0.1.0] - 09/09/2026

* ⭐ Initial release
