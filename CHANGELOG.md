# Changelog

## [Unreleased]

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
* 🪲 An empty drawable renders as a blank image instead of failing in the rasterizer


## [v0.1.0] - 09/09/2026s

* ⭐ Initial release
