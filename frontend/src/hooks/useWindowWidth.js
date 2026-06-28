import { useState, useEffect } from 'react'

export function useWindowWidth() {
    const [width, setWidth] = useState(window.innerWidth)

    useEffect(() => {
        const handler = () => setWidth(window.innerWidth)
        window.addEventListener('resize', handler)
        return () => window.removeEventListener('resize', handler)
    }, [])

    return width
}

/* Convenience: true when viewport is below 768px */
export function useIsMobile() {
    return useWindowWidth() < 768
}
