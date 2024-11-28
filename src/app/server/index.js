import realServer from './axios'
import dummyServer from './dummy'

const mode = import.meta.env.MODE
let server = realServer
export default server