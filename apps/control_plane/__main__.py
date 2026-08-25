import uvicorn


def main() -> None:
    uvicorn.run("apps.control_plane.app:app", host="0.0.0.0", port=8090, reload=False)


if __name__ == "__main__":
    main()
