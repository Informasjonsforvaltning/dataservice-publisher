# TODO

- [x] Add poetry to manage dependencies
- [x] Add nox tool to automate testing
- [x] Add linting to nox
- [x] Add unit and integration tests
- [x] Add coverage
- [x] Use ~~datacatalogtordf~~ oastodcat to do the conversion from json to rdf at create (POST) time. Add to triple store (in memory)
- [x] Respond with rdf fetched from repositoy by sparql queries via SPARQLWrapper
- [ ] Refactor towards [Architecture Patterns with Python](https://www.oreilly.com/library/view/architecture-patterns-with/9781492052197/)
  - [ ] Domain model pattern
  - [ ] Repository pattern
  - [ ] Service layer pattern
  - [ ] Unit of Work (UoW) pattern
  - [ ] Aggregate pattern
- [x] Refactor to aiohttp framework
