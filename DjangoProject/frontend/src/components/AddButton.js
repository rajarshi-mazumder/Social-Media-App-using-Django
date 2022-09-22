import React from 'react'
import { Link } from 'react-router-dom'
import { ReactComponent as AddIcon } from '../assets/plus.svg'

const AddButton = () => {
    return (
        <Link to="/post/new" className='floating-button'>
            <AddIcon />
        </Link>
    )
}

export default AddButton
