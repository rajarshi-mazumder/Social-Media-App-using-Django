import React from 'react'
import { Link } from 'react-router-dom'

const PostItem = (props) => {
    return (
        <Link to={`/post/${props.id}`}>
            <div className='notes-list-item'>
                <h3>{props.id} {props.body}</h3>
            </div>


        </Link>
    )
}

export default PostItem
