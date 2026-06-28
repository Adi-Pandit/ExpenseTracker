/* Ledgerly mark: indigo rounded box with a rotated white diamond inside */
export default function Logo({ size = 34, bg = 'var(--primary)', color = '#fff' }) {
    const r = Math.round(size * 0.29)
    const diamond = Math.round(size * 0.41)
    const diamondR = Math.round(size * 0.12)

    return (
        <div style={{
            width: size,
            height: size,
            borderRadius: r,
            background: bg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
        }}>
            <div style={{
                width: diamond,
                height: diamond,
                borderRadius: diamondR,
                background: color,
                transform: 'rotate(45deg)',
            }} />
        </div>
    )
}
