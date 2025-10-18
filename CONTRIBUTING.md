# Contributing Guidelines

Thank you for your interest in contributing to this Flutter + Rust hybrid project!

## Development Setup

1. Install prerequisites as documented in [README.md](README.md)
2. Clone the repository
3. Run the setup script:
   ```bash
   make setup
   ```

## Code Style

### Dart/Flutter
- Follow the [official Dart style guide](https://dart.dev/guides/language/effective-dart/style)
- Use `flutter format` to format Dart code
- Run `flutter analyze` to check for issues
- Prefer composition over inheritance
- Use meaningful variable and function names

### Rust
- Follow the [official Rust style guide](https://doc.rust-lang.org/1.0.0/style/)
- Use `cargo fmt` to format Rust code
- Run `cargo clippy` for linting
- Write tests for all public APIs
- Document public functions with doc comments

### C++
- Follow Google C++ Style Guide
- Use 2-space indentation
- Prefer const correctness

## Project Structure

```
/app      - Flutter application code
/core     - Rust business logic
/bridge   - FFI bindings layer
```

## Making Changes

1. Create a new branch for your feature or bugfix
2. Make your changes following the code style guidelines
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request

## Testing

### Rust Tests
```bash
cd core
cargo test
```

### Flutter Tests
```bash
cd app
flutter test
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Example:
```
feat: add user authentication in Rust core

- Implement JWT token generation
- Add user session management
- Update bridge bindings
```

## Pull Request Process

1. Ensure all tests pass
2. Update the README.md with details of changes if needed
3. Update the CHANGELOG.md (if present)
4. The PR will be merged once you have approval from maintainers

## Questions?

Feel free to open an issue for any questions or concerns.
