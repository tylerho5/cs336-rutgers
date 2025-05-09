# Natural Language Database Interface

This project implements a natural language interface to a PostgreSQL database using Next.js for the frontend and FastAPI for the backend. The system uses two LLMs (Phi-3.5-mini and sqlcoder-7b-2) to convert natural language queries into SQL and execute them.

## Features Implemented

- ✅ Basic working frontend that provides a textbox for natural language queries and displays the output
- ✅ Organized interactive tables that can be sorted by clicking on column headers
- ✅ Separate displays for SQL query, LLM output, and query results
- ✅ Modern, attractive interface with clean design and responsive layout
- ✅ Error handling and feedback to the user

## Setup and Running

### 1. Set up and start the backend

Make sure the backend is running. Navigate to the `project_2` directory (one level up from this `ec-frontend-nextjs` folder) and follow the instructions in `project_2/README.md` or use the main `run_ec_project.sh` script.

Typically, from the `cs336-rutgers/project_2` directory:

```bash
# Activate the virtual environment (if not already active from run_ec_project.sh)
# source CS336P2/bin/activate

# Navigate to the backend directory (now project_2/backend)
cd backend

# Start the FastAPI server
KMP_DUPLICATE_LIB_OK=TRUE python3 main.py
```

The backend should be running at http://localhost:8000

### 2. Set up and start the frontend (this project)

```bash
# Navigate to this frontend directory (project_2/ec-frontend-nextjs)
# cd ec-frontend-nextjs # If you are not already here

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at http://localhost:3000

Alternatively, you can run both backend and frontend using the main script from the `cs336-rutgers` root directory:
```bash
# From the cs336-rutgers directory
./project_2/run_ec_project.sh
```

## How It Works

1. The user enters a natural language query in the textbox
2. The frontend sends the query to the backend API
3. The backend uses the LLMs to:
   - Convert natural language to relational algebra
   - Convert relational algebra to SQL
4. The query is executed on the Rutgers database through SSH tunneling
5. Results are returned to the frontend and displayed in an interactive table

## Interface Components

- **Query Input**: A textbox with a submit button for entering natural language queries
- **Results Display**: Tabbed interface with:
  - Interactive table with sortable columns 
  - SQL query view showing both relational algebra and SQL
  - LLM output view showing the raw LLM response
- **Error Handling**: Friendly error messages displayed to the user

## Technologies Used

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **LLMs**: Phi-3.5-mini, sqlcoder-7b-2
- **Database**: PostgreSQL (accessed via SSH tunneling)

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
