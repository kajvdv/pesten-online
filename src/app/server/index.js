import realServer from './axios'
import dummyServer from './dummy'

const mode = import.meta.env.MODE
let server = realServer
if (mode === 'development') {
    console.log("Using development server")
    server = dummyServer
}
export default server