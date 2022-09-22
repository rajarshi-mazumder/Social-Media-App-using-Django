import React, { useState, useEffect } from 'react'
import PostItem from '../components/PostItem'
import AddButton from '../components/AddButton'

const PostsListsPage = () => {
    let [posts, setPosts] = useState([])
    useEffect(() => {
        getPosts()
    }, [])

    let getPosts = async () => {
        let response = await fetch('/getPosts/')
        let data = await response.json()

        setPosts(data)
    }


    const postElements = posts.map(post => {
        return <PostItem key={post.id} body={post.body} id={post.id} />
    })
    return (
        <div className='notes'>
            <div className='notes-header'>
                <h2 className='notes-title'>&#9782; Posts</h2>
                <p className='notes-count'>{posts.length}</p>
            </div>
            <div className='notes-list'>
                {postElements}


            </div>
            <AddButton />
        </div>
    )
}

export default PostsListsPage
