import React, { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom';
import { ReactComponent as ArrowLeft } from '../assets/arrow-left.svg'

const PostPage = () => {
    let navigate = useNavigate()
    let { id } = useParams();
    let [post, setPost] = useState(null)

    useEffect(() => {
        getPost()
    }, [id])

    let getPost = async () => {
        if (id === 'new') return
        let response = await fetch(`/getPosts/${id}`)
        let data = await response.json()
        setPost(data)
    }

    let updatePost = async () => {
        fetch(`/getPosts/${id}/update`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(post)
        })
    }

    let deletePost = async () => {
        fetch(`/getPosts/${id}/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        navigate("/")
    }

    let handleSubmit = () => {
        updatePost()
        navigate("/")
    }
    return (
        <div className='note'>
            <div className='note-header'>
                <h3>
                    <Link to="/">
                        <ArrowLeft onClick={handleSubmit} />
                    </Link>
                    {id != 'new' ? (
                        <button onClick={deletePost}>Delete</button>
                    ) : (
                        <button onClick={deletePost}>Done</button>
                    )}
                </h3>

            </div>
            <textarea onChange={(e) => { setPost({ ...post, 'body': e.target.value }) }} defaultValue={post?.body}></textarea>
            <button onClick={handleSubmit}>Submit</button>

        </div>
    )
}

export default PostPage
