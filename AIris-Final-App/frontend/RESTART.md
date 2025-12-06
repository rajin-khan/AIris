# If you see import errors, try this:

1. Stop the dev server (Ctrl+C or Cmd+C)

2. Clear Vite cache:
```bash
rm -rf node_modules/.vite
```

3. Restart the dev server:
```bash
npm run dev
```

If that doesn't work, try:
```bash
rm -rf node_modules/.vite dist
npm run dev
```


