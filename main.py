# TASK 8

# Personal Portfolio API:

# Develop a fully functional API for a personal portfolio website, 
# including endpoints for projects (add, edit, delete,all project, single project), 
# blog posts (add, edit, delete,all blog posts, single blog post), 
# and contact information (add, edit, delete). 
# Use SQLite as a database. 




from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

# Data models
class Project(BaseModel):
    id: int
    title: str
    description: str
    link: str

{
    "id": 1,
    "title": "Project X",
    "description": "My First FastAPI Project",
    "link": "https://sample.com"
}


class BlogPost(BaseModel):
    id: int
    title: str
    content: str

{
    "id": 1,
    "title": "Blog Post X",
    "content": "How to make a blog post"
}

class Contact(BaseModel):
    id: int
    name: str
    email: str
    message: str

{
    "id": 1,
    "name": "Chimaobi Onwuegbu",
    "email": "chimaobi@sample.com",
    "message": "The Virtuoso Organist"
}


# SQLite database Connection
conn = sqlite3.connect('portfolio.db', check_same_thread=False)
c = conn.cursor()

# Necessary tables
c.execute('''CREATE TABLE IF NOT EXISTS projects
             (id INTEGER PRIMARY KEY, title TEXT, description TEXT, link TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS blog_posts
             (id INTEGER PRIMARY KEY, title TEXT, content TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS contacts
             (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)''')
conn.commit()


# PROJECTS ENDPOINTS

# ADD PROJECT ENDPOINT
@app.post("/projects", response_model=Project)
def create_project(project: Project):
    c.execute("INSERT INTO projects (title, description, link) VALUES (?, ?, ?)", (project.title, project.description, project.link))
    conn.commit()
    project.id = c.lastrowid
    return project

@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: int):
    c.execute("SELECT id, title, description, link FROM projects WHERE id = ?", (project_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(id=data[0], title=data[1], description=data[2], link=data[3])

@app.get("/projects", response_model=List[Project])
def get_all_projects():
    c.execute("SELECT id, title, description, link FROM projects")
    data = c.fetchall()
    return [Project(id=row[0], title=row[1], description=row[2], link=row[3]) for row in data]


# PROJECT MODIFICATION ENDPOINTS -> EDIT AND DELETE

# EDIT PROJECT ENDPOINT
@app.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project: Project):
    c.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Project not found")

    c.execute("UPDATE projects SET title = ?, description = ?, link = ? WHERE id = ?",
              (project.title, project.description, project.link, project_id))
    conn.commit()
    return Project(id=project_id, title=project.title, description=project.description, link=project.link)

# DELETE PROJECT ENDPOINT
@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    c.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Project not found")

    c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    return {"message": "Project deleted"}



# BLOG POST ENDPOINTS

# ADD BLOG POST ENDPOINT
@app.post("/blogposts", response_model=BlogPost)
def create_blogpost(blogpost: BlogPost):
    c.execute("INSERT INTO blog_posts (title, content) VALUES (?, ?)", (blogpost.title, blogpost.content))
    conn.commit()
    blogpost.id = c.lastrowid
    return blogpost

@app.get("/blogposts/{blogpost_id}", response_model=BlogPost)
def get_blogpost(blogpost_id: int):
    c.execute("SELECT id, title, content FROM blog_posts WHERE id = ?", (blogpost_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="BlogPost not found")
    return BlogPost(id=data[0], title=data[1], content=data[2])

@app.get("/blogposts", response_model=List[BlogPost])
def get_all_blogposts():
    c.execute("SELECT id, title, content FROM blog_posts")
    data = c.fetchall()
    return [BlogPost(id=row[0], title=row[1], content=row[2]) for row in data]


# BLOGPOST MODIFICATION -> EDIT AND DELETE

# EDIT BLOG POST ENDPOINT
@app.put("/blogposts/{blogpost_id}", response_model=BlogPost)
def update_blogpost(blogpost_id: int, blogpost: BlogPost):
    c.execute("SELECT id FROM blog_posts WHERE id = ?", (blogpost_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="BlogPost not found")

    c.execute("UPDATE blog_posts SET title = ?, content = ? WHERE id = ?",
              (blogpost.title, blogpost.content, blogpost_id))
    conn.commit()
    return BlogPost(id=blogpost_id, title=blogpost.title, content=blogpost.content)

# DELETE BLOG POST ENDPOINT
@app.delete("/blogposts/{blogpost_id}")
def delete_blogpost(blogpost_id: int):
    c.execute("SELECT id FROM blog_posts WHERE id = ?", (blogpost_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="BlogPost not found")

    c.execute("DELETE FROM blog_posts WHERE id = ?", (blogpost_id,))
    conn.commit()
    return {"message": "BlogPost deleted"}




# CONTACT ENDPOINTS

# ADD CONTACT ENDPOINT
@app.post("/contacts", response_model=Contact)
def create_contact(contact: Contact):
    c.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)", (contact.name, contact.email, contact.message))
    conn.commit()
    contact.id = c.lastrowid
    return contact

@app.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(contact_id: int):
    c.execute("SELECT id, name, email, message FROM contacts WHERE id = ?", (contact_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return Contact(id=data[0], name=data[1], email=data[2], message=data[3])

@app.get("/contacts", response_model=List[Contact])
def get_all_contact():
    c.execute("SELECT id, name, email, message FROM contacts")
    data = c.fetchall()
    return [Contact(id=row[0], name=row[1], email=row[2], message=row[2]) for row in data]



# CONTACT MODIFICATION -> EDIT AND DELETE

# EDIT CONTACT ENDPOINT
@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: Contact):
    c.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    c.execute("UPDATE contacts SET name = ?, email = ?, message = ? WHERE id = ?",
              (contact.name, contact.email, contact.message, contact_id))
    conn.commit()
    return Contact(id=contact_id, name=contact.name, email=contact.email, message=contact.message)

# DELETE CONTACT ENDPOINT
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int):
    c.execute("SELECT id FROM contacts WHERE id = ?", (contact_id,))
    data = c.fetchone()
    if data is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    c.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    return {"message": "Contact deleted"}