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

```bash
# Navigate to the backend directory
cd backend

# Activate the virtual environment from project_2
source ../project_2/CS336P2/bin/activate

# Start the FastAPI server
python main.py
```

The backend will be running at http://localhost:8000

### 2. Set up and start the frontend

```bash
# Navigate to the frontend directory
cd ec-frontend-nextjs

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be running at http://localhost:3000

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
