# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler not enabled

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

To Run
backend -> uvicorn app.main:app --reload --port 8000
frontend -> npm run dev
CommunityLibrary -> ngrok http 5173


Requirements
1. Infra
2. Google books API key
SMTP - google app, email id and password

ToDo
Profile page - update details - my books, borrowed books, add books
dashboard keep minimal - communities and search, requests, lent
Admin approve/reject request and page
Return Request
borrow request reverted after 15 days
barcode scanner for isbn, bulk upload 
automated app like login/logout from browser