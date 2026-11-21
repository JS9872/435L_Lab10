"""Greeting application for EECE 435L Lab 10."""


def greet(name):
    """Return a greeting signed by the student."""
    return f"Hello, {name} from Joey Saade!"


def main():
    """Run the application."""
    print(greet("World"))


if __name__ == "__main__":
    main()
