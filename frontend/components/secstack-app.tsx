'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { create } from 'zustand'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft, ArrowUpRight, Bookmark, ChevronRight, Download,
  FileText, Grid2X2, LayoutList, Menu, Orbit, Search, Sparkles,
  Terminal, X, Zap, Loader2, RefreshCw, ShieldAlert, Trash2, Trophy, Key,
  Activity
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  getGalaxy, getCategories, getResources, getResourceById,
  getPlanetDetail, getClusterStats, getStatsTimeseries, getStatsSources,
  getBookmarks, syncBookmarks, triggerIngest, getClientScore, submitCtfTaskFlag,
  getHint, getLeaderboard, getAgentRuns, getAgentRunDetail, deleteAgentRun,
  getHarnessManifest, createCtfRoom, downloadRunArchive, getPublisherStats,
  GalaxyData, ResourceItem
} from '@/lib/api'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Helper for persistent client ID
function getClientId(): string {
  if (typeof window === 'undefined') return 'server-client'
  try {
    let id = localStorage.getItem('secstack_client_id')
    if (!id) {
      id = 'client_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
      localStorage.setItem('secstack_client_id', id)
    }
    return id
  } catch {
    return 'anon-client'
  }
}

function downloadFile(filename: string, content: string, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

type GalaxyState = {
  focused: string | null
  savedResourceIds: string[]
  notes: Record<string, string>
  hydrated: boolean
  focus: (slug: string | null) => void
  toggleSaved: (resourceId: string) => void
  setNote: (resourceId: string, note: string) => void
  setSavedIds: (ids: string[]) => void
  hydrate: (ids: string[], notes: Record<string, string>) => void
}

export const useGalaxyStore = create<GalaxyState>((set, get) => ({
  focused: null,
  savedResourceIds: [],
  notes: {},
  hydrated: false,
  focus: (focused) => set({ focused }),
  toggleSaved: (resourceId) => {
    const ids = get().savedResourceIds
    const nextIds = ids.includes(resourceId)
      ? ids.filter((id) => id !== resourceId)
      : [...ids, resourceId]
    set({ savedResourceIds: nextIds })
    const clientId = getClientId()
    syncBookmarks(
      clientId,
      nextIds.map((rid) => ({ resource_id: rid, note: get().notes[rid] || '', client_id: clientId }))
    ).catch((err) => console.error('Sync error:', err))
  },
  setNote: (resourceId, note) => {
    set((state) => ({ notes: { ...state.notes, [resourceId]: note } }))
  },
  setSavedIds: (ids) => set({ savedResourceIds: ids }),
  hydrate: (ids, notes) => set({ savedResourceIds: ids, notes, hydrated: true }),
}))

// ---------------------------------------------------------------------------
// Layout
// ---------------------------------------------------------------------------

function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [menu, setMenu] = useState(false)
  const hydrated = useGalaxyStore((s) => s.hydrated)
  const hydrate = useGalaxyStore((s) => s.hydrate)

  const nav: Array<[string, string]> = [
    ['/', 'Galaxy'],
    ['/ctf', 'Matrix'],
    ['/index', 'Index'],
    ['/analytics', 'Analytics'],
    ['/saved', 'Saved'],
    ['/signal', 'Signal'],
    ['/tracks', 'Tracks'],
    ['/about', 'About'],
  ]

  // Load bookmarks once so the saved state is correct on every page, not only /saved.
  useEffect(() => {
    if (hydrated) return
    getBookmarks(getClientId())
      .then((res) => {
        const b: any[] = res?.bookmarks || []
        const n: Record<string, string> = {}
        b.forEach((x) => { if (x.note) n[x.resource_id] = x.note })
        hydrate(b.map((x) => x.resource_id), n)
      })
      .catch(() => {})
  }, [hydrated, hydrate])

  // Make the advertised ⌘K / Ctrl+K shortcut actually work.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        router.push('/index')
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [router])

  return (
    <main className="app-shell">
      <div className="starfield" aria-hidden="true" />
      <div className="nebula nebula-left" />
      <div className="nebula nebula-right" />
      <div className="scanlines" />
      <header className="topbar">
        <Link className="brand" href="/">
          <span className="brand-mark"><Orbit /></span>
          <span>SEC<span>STACK</span></span>
        </Link>
        <Link href="/index" className="header-search" style={{ textDecoration: 'none', color: 'inherit' }}>
          <Search />
          <span>Search the security universe...</span>
          <kbd>⌘ K</kbd>
        </Link>
        <button className="menu-button" onClick={() => setMenu(!menu)} aria-label="Toggle navigation">
          <Menu />
        </button>
        <nav className={menu ? 'nav-links nav-open' : 'nav-links'}>
          {nav.map(([href, label]) => (
            <Link key={href} className={pathname === href ? 'active' : ''} href={href} onClick={() => setMenu(false)}>
              {label}
            </Link>
          ))}
        </nav>
        <Link href="/signal">
          <Button className="signal-button"><Zap data-icon="inline-start" /> Signal</Button>
        </Link>
      </header>
      {children}
      <footer>
        <div className="brand">
          <span className="brand-mark"><Orbit /></span>
          <span>SEC<span>STACK</span></span>
        </div>
        <span className="footer-copy">A living map of the cybersecurity universe.</span>
        <span className="footer-mono">SYS.STATUS: <b>OPERATIONAL</b></span>
      </footer>
    </main>
  )
}

function PlanetVisual({ planet, large = false }: { planet: { color: string; top_terms?: string[] }; large?: boolean }) {
  const terms = planet.top_terms && planet.top_terms.length >= 3 ? planet.top_terms : ['telemetry', 'resilience', 'protocols']
  return (
    <div className={large ? 'planet-visual planet-visual-large' : 'planet-visual'} style={{ '--planet-color': planet.color } as React.CSSProperties}>
      <div className="planet-aura" />
      <div className="planet-surface"><span /><span /><span /></div>
      <div className="planet-orbit orbit-a"><i>{terms[0]}</i></div>
      <div className="planet-orbit orbit-b"><i>{terms[1]}</i></div>
      <div className="planet-orbit orbit-c"><i>{terms[2]}</i></div>
    </div>
  )
}

function ResourceCard({ resource }: { resource: ResourceItem }) {
  const saved = useGalaxyStore((s) => s.savedResourceIds.includes(resource.id))
  const toggle = useGalaxyStore((s) => s.toggleSaved)

  const formattedDate = resource.published_day || 'Recent'
  const readTime = resource.read_time_min ? `${resource.read_time_min} min` : '5 min'
  const typeLabel = (resource.media_type || 'RESOURCE').toUpperCase()

  return (
    <motion.article
      whileHover={{ y: -5, boxShadow: '0 0 20px rgba(0,240,255,0.2)' }}
      className="resource-card"
      onClick={() => window.open(resource.url, '_blank', 'noopener,noreferrer')}
      style={{ cursor: 'pointer' }}
    >
      <div className="resource-topline">
        <span style={{ color: '#00f0ff' }}>● {typeLabel}</span>
        <span>{formattedDate}</span>
      </div>
      <h3>{resource.title}</h3>
      <div className="resource-meta">
        <span className="domain-mark" style={{ background: '#00f0ff' }} />
        {resource.source || 'web'}
        <span>·</span>
        {readTime} read
      </div>
      <div className="tag-row">
        {resource.tags && resource.tags.slice(0, 3).map((tag) => <span key={tag}>#{tag}</span>)}
      </div>
      <button
        className={`save-button ${saved ? 'is-saved' : ''}`}
        onClick={(e) => { e.stopPropagation(); toggle(resource.id) }}
        aria-label={saved ? 'Remove saved resource' : 'Save resource'}
      >
        <Bookmark fill={saved ? 'currentColor' : 'none'} />
      </button>
      <ArrowUpRight className="card-arrow" />
    </motion.article>
  )
}

function PageFrame({ title, kicker, children }: { title: string; kicker: string; children: React.ReactNode }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="page-frame"
    >
      <Link href="/" className="back-link"><ArrowLeft /> Back to galaxy</Link>
      <div className="eyebrow"><span className="eyebrow-line" /> {kicker}</div>
      <h1>{title}</h1>
      {children}
    </motion.section>
  )
}

// Was referenced in SecStackApp but never defined.
function SimplePage({ title, kicker, copy, tracks = false }: { title: string; kicker: string; copy: string; tracks?: boolean }) {
  const trackList = [
    { name: 'Security+ Foundations', level: 'Beginner', focus: 'Core concepts, threats, and controls' },
    { name: 'Blue Team / SOC Analyst', level: 'Intermediate', focus: 'Detection, triage, and incident response' },
    { name: 'Penetration Testing', level: 'Intermediate', focus: 'Recon, exploitation, and reporting' },
    { name: 'Cloud & Application Security', level: 'Advanced', focus: 'Secure design, IAM, and DevSecOps' },
  ]
  return (
    <PageFrame title={title} kicker={kicker}>
      <p style={{ color: '#aaa', maxWidth: '640px', lineHeight: 1.7 }}>{copy}</p>
      {tracks && (
        <div className="resource-grid" style={{ marginTop: '24px' }}>
          {trackList.map((t) => (
            <article key={t.name} className="resource-card">
              <div className="resource-topline"><span style={{ color: '#00f0ff' }}>● {t.level.toUpperCase()}</span></div>
              <h3>{t.name}</h3>
              <div className="resource-meta">{t.focus}</div>
            </article>
          ))}
        </div>
      )}
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// Galaxy
// ---------------------------------------------------------------------------

function Galaxy() {
  const focused = useGalaxyStore((s) => s.focused)
  const focus = useGalaxyStore((s) => s.focus)
  const [galaxyData, setGalaxyData] = useState<GalaxyData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getGalaxy()
      .then((data) => {
        setGalaxyData(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message || 'Failed to load galaxy data')
        setLoading(false)
      })
  }, [])

  const selected = galaxyData?.planets.find((p) => p.slug === focused)

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', color: '#00f0ff', gap: '12px' }}>
        <Loader2 className="animate-spin" /> SYNCHRONIZING GALAXY CORE...
      </div>
    )
  }

  if (error || !galaxyData) {
    return (
      <div style={{ padding: '4rem', textAlign: 'center', color: '#ff2d95' }}>
        <ShieldAlert size={48} style={{ margin: '0 auto 16px' }} />
        <h2>GALAXY INITIALIZATION OFFLINE</h2>
        <p style={{ color: '#888', marginTop: '8px' }}>{error || 'Could not connect to backend cluster.'}</p>
        <Button onClick={() => window.location.reload()} style={{ marginTop: '20px' }}><RefreshCw data-icon="inline-start" /> RECONNECT</Button>
      </div>
    )
  }

  return (
    <>
      <section className={`hero ${selected ? 'has-focus' : ''}`} id="galaxy">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-line" /> SECURITY KNOWLEDGE CORE</div>
          <h1>Navigate the<br /><em>security</em> universe.</h1>
          <p>Every resource is a star. Every discipline, a planet.<br />Find your next breakthrough in the galaxy of cybersecurity.</p>
          <div className="hero-actions">
            <Button className="primary-cta" onClick={() => document.getElementById('resource-feed')?.scrollIntoView({ behavior: 'smooth' })}>
              EXPLORE THE GALAXY
            </Button>
            <Link href="/index">
              <Button variant="outline" className="ghost-cta"><Terminal data-icon="inline-start" /> OPEN INDEX</Button>
            </Link>
          </div>
        </div>
        <div className="galaxy-stage" aria-label="Interactive cybersecurity galaxy" style={{ position: 'relative', width: '100%', height: '480px' }}>
          <div className="galaxy-core" />
          {galaxyData.planets.map((p, i) => (
            <motion.button
              key={p.slug}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: i * 0.1, type: 'spring' }}
              className={`planet planet-orbit-${i % 6} ${focused === p.slug ? 'planet-selected' : ''}`}
              // framer-motion owns `transform`, so centering must go through x/y,
              // otherwise a CSS translate() gets overwritten by the scale animation.
              style={{
                '--planet-color': p.color,
                left: `${p.cx}%`,
                top: `${p.cy}%`,
                position: 'absolute',
                x: '-50%',
                y: '-50%',
              } as any}
              onClick={() => focus(p.slug)}
              aria-label={`Focus ${p.name}`}
            >
              <span className="planet-glow" />
              <span className="planet-core" />
              <span className="planet-ring ring-one" />
              <span className="planet-label">
                <strong>{p.name}</strong>
                <small>{p.resource_count} SIGNALS</small>
              </span>
              <span className="moon moon-a" />
              <span className="moon moon-b" />
            </motion.button>
          ))}
        </div>
      </section>

      <AnimatePresence>
        {selected && (
          <motion.section
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="focus-dock"
          >
            <div className="focus-orb"><PlanetVisual planet={selected} /></div>
            <div>
              <div className="eyebrow"><span className="pulse-dot" /> FOCUS LOCK // {selected.slug.toUpperCase()}</div>
              <h2>{selected.name}</h2>
              <p>{selected.resource_count} signals indexed. Satellite moons are synchronized to the live knowledge graph.</p>
              <Link className="primary-cta focus-link" href={`/planet/${selected.slug}`}>
                OPEN COMMAND CENTER <ChevronRight />
              </Link>
            </div>
            <button className="focus-close" onClick={() => focus(null)} aria-label="Close focus dock"><X /></button>
          </motion.section>
        )}
      </AnimatePresence>

      <section className="resource-feed" id="resource-feed">
        <div className="section-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-line" /> LIVE KNOWLEDGE FEED</div>
            <h2>Discovered signals</h2>
          </div>
          <Link href="/index"><Button variant="outline" className="ghost-cta">View full index <ArrowUpRight /></Button></Link>
        </div>
        <GalaxyFeedPreview />
      </section>
    </>
  )
}

function GalaxyFeedPreview() {
  const [items, setItems] = useState<ResourceItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getResources({ page_size: 4, sort: 'recent' })
      .then((res) => {
        setItems(res?.items || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ color: '#888', padding: '20px' }}>Loading feed...</div>
  if (!items.length) return <div style={{ color: '#888', padding: '20px' }}>No resources indexed yet.</div>

  return (
    <div className="resource-grid">
      {items.map((item) => <ResourceCard key={item.id} resource={item} />)}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Planet detail
// ---------------------------------------------------------------------------

export function PlanetDetail({ slug }: { slug: string }) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tuning, setTuning] = useState(false)
  const [tuneMessage, setTuneMessage] = useState<string | null>(null)

  const fetchPlanet = () => {
    setLoading(true)
    setError(null)
    getPlanetDetail(slug)
      .then((res) => {
        setData(res)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message || 'Planet not found')
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchPlanet()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug])

  const handleTuneSignal = async () => {
    setTuning(true)
    setTuneMessage('Ingesting live RSS feeds & clustering...')
    try {
      const res = await triggerIngest()
      setTuneMessage(`Successfully ingested ${res?.new_signals ?? 0} new live signals!`)
      fetchPlanet()
    } catch (err: any) {
      setTuneMessage(`Ingestion failed: ${err.message}`)
    } finally {
      setTuning(false)
    }
  }

  if (loading && !data) {
    return (
      <PageFrame title={slug} kicker="PLANETARY COMMAND CENTER">
        <div style={{ color: '#00f0ff', padding: '40px' }}>Syncing orbital telemetry for {slug}...</div>
      </PageFrame>
    )
  }

  if (error || !data) {
    return (
      <PageFrame title={slug} kicker="PLANETARY COMMAND CENTER">
        <div style={{ color: '#ff2d95', padding: '40px' }}>Planet telemetry unavailable: {error}</div>
      </PageFrame>
    )
  }

  const { cluster, resource_count, avg_read_time, top_resources = [] } = data
  const terms: string[] = cluster.top_terms || ['telemetry', 'resilience', 'protocols']
  // PlanetVisual expects `top_terms` (the original passed `terms`, so it always fell back to defaults).
  const planet = { name: cluster.label, color: cluster.color, top_terms: terms }
  const weights = [0.94, 0.81, 0.68, 0.54, 0.42, 0.35, 0.28]

  const exportPlanetMarkdown = () => {
    let md = `# SecStack Intelligence Report: ${cluster.label}\n\n`
    md += `- **Silhouette Score:** ${cluster.silhouette_score ?? 0.82}\n`
    md += `- **Total Signals:** ${resource_count}\n`
    md += `- **Average Read Time:** ${avg_read_time}m\n`
    md += `- **Top Terms:** ${terms.join(', ')}\n\n`
    md += `## Top Orbital Signals\n\n`
    top_resources.forEach((r: any, idx: number) => {
      md += `### ${idx + 1}. [${r.title}](${r.url})\n`
      md += `- **Source:** ${r.source}\n`
      md += `- **Category:** ${r.category}\n\n`
    })
    downloadFile(`secstack-${cluster.slug || slug}-report.md`, md, 'text/markdown')
  }

  return (
    <PageFrame title={cluster.label} kicker="PLANETARY COMMAND CENTER">
      <div className="planet-command">
        <div className="command-visual">
          <PlanetVisual planet={planet} large />
          <div className="visual-readout">
            <span>ROTATION</span><b>0.84 RPM</b>
            <span>AVG READ</span><b>{avg_read_time}m</b>
            <span>INDEX</span><b>{resource_count} SIGNALS</b>
          </div>
        </div>
        <div className="hud-panel">
          <div className="hud-top">
            <span className="panel-kicker">[ ACCESS GRANTED ] // LIVE TELEMETRY</span>
            <span className="hud-status">● LINKED</span>
          </div>
          <h2>Signal intelligence</h2>
          <p className="hud-copy">{cluster.description || 'Tracking core concepts and emerging patterns across this discipline.'}</p>
          <div className="telemetry-grid">
            <div><span>SILHOUETTE</span><b>{cluster.silhouette_score ?? '0.82'}</b></div>
            <div><span>SIGNALS</span><b>{resource_count}</b></div>
            <div><span>COHESION</span><b>0.91</b></div>
            <div><span>AVG READ</span><b>{avg_read_time}m</b></div>
          </div>
          <div className="term-weights">
            <div className="panel-kicker">TF-IDF TERM WEIGHTS</div>
            {cluster.top_terms_weighted ? (
              cluster.top_terms_weighted.map((tw: any) => (
                <div className="weight-row" key={tw.term}>
                  <span>{tw.term}</span>
                  <i><motion.b initial={{ width: 0 }} animate={{ width: `${tw.weight * 100}%` }} style={{ background: cluster.color }} /></i>
                  <strong>{Number(tw.weight).toFixed(2)}</strong>
                </div>
              ))
            ) : (
              terms.map((term: string, i: number) => (
                <div className="weight-row" key={term}>
                  <span>{term}</span>
                  <i><motion.b initial={{ width: 0 }} animate={{ width: `${weights[i % weights.length] * 100}%` }} style={{ background: cluster.color }} /></i>
                  <strong>{weights[i % weights.length].toFixed(2)}</strong>
                </div>
              ))
            )}
          </div>
          <div className="quick-actions" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <Button className="primary-cta" onClick={handleTuneSignal} disabled={tuning}>
                {tuning ? <Loader2 className="animate-spin" /> : <Sparkles data-icon="inline-start" />}
                {tuning ? 'Tuning...' : 'TUNE SIGNAL (LIVE)'}
              </Button>
              <Button variant="outline" className="ghost-cta" onClick={exportPlanetMarkdown}>
                <Download data-icon="inline-start" /> EXPORT .MD
              </Button>
            </div>
            {tuneMessage && <small style={{ color: tuneMessage.includes('failed') ? '#ff2d95' : '#22ff88' }}>{tuneMessage}</small>}
          </div>
        </div>
      </div>

      <div className="command-feed">
        <div className="section-heading">
          <div>
            <div className="eyebrow"><span className="eyebrow-line" /> ORBITAL RESOURCE MOONS</div>
            <h2>Signals in orbit</h2>
          </div>
          <span className="live-pill">LIVE TREND +18.4%</span>
        </div>
        <div className="resource-grid">
          {top_resources.map((r: any) => (
            <ResourceCard key={r.id} resource={r} />
          ))}
        </div>
      </div>
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// Index
// ---------------------------------------------------------------------------

function IndexView() {
  const [grid, setGrid] = useState(true)
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [categories, setCategories] = useState<any[]>([])
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCategories().then((c) => setCategories(c || [])).catch(() => {})
  }, [])

  // Debounce typing so we don't fire a request per keystroke.
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(t)
  }, [query])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    getResources({ category, q: debouncedQuery, page_size: 40 })
      .then((res) => {
        if (cancelled) return
        setResources(res?.items || [])
        setLoading(false)
      })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [category, debouncedQuery])

  return (
    <PageFrame title="The Index" kicker="CURATED RESOURCE INDEX">
      <div className="planet-badges" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
        <button
          onClick={() => setCategory(undefined)}
          style={{ background: !category ? '#00f0ff' : 'rgba(255,255,255,0.05)', color: !category ? '#000' : '#fff', padding: '6px 14px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.1)', cursor: 'pointer', fontSize: '0.85rem' }}
        >
          All Categories
        </button>
        {categories.map((p) => (
          <button
            key={p.slug}
            onClick={() => setCategory(p.slug)}
            style={{ background: category === p.slug ? p.color : 'rgba(255,255,255,0.05)', color: category === p.slug ? '#000' : '#fff', padding: '6px 14px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.1)', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}
          >
            <span className="mini-planet" style={{ background: p.color, width: '8px', height: '8px', borderRadius: '50%', display: 'inline-block' }} />
            {p.name} ({p.count})
          </button>
        ))}
      </div>

      <div className="toolbar">
        <div className="header-search">
          <Search />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter signals..." />
        </div>
        <div className="view-toggle">
          <button className={grid ? 'selected' : ''} onClick={() => setGrid(true)} aria-label="Card grid"><Grid2X2 /></button>
          <button className={!grid ? 'selected' : ''} onClick={() => setGrid(false)} aria-label="Data table"><LayoutList /></button>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: '#00f0ff' }}>Querying index database...</div>
      ) : resources.length === 0 ? (
        <div style={{ padding: '60px', textAlign: 'center', color: '#888' }}>No matching signals found.</div>
      ) : grid ? (
        <div className="resource-grid">
          {resources.map((r) => <ResourceCard key={r.id} resource={r} />)}
        </div>
      ) : (
        <div className="data-table">
          {resources.map((r, i) => (
            <div className="data-row" key={r.id} onClick={() => window.open(r.url, '_blank', 'noopener,noreferrer')} style={{ cursor: 'pointer' }}>
              <span>{String(i + 1).padStart(2, '0')}</span>
              <strong>{r.title}</strong>
              <span>{r.category}</span>
              <span>{r.read_time_min ? `${r.read_time_min}m` : '5m'}</span>
              <ArrowUpRight />
            </div>
          ))}
        </div>
      )}
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

function Analytics() {
  const [sources, setSources] = useState<any[]>([])
  const [timeseries, setTimeseries] = useState<any[]>([])
  const [clusters, setClusters] = useState<any[]>([])
  const [pubStats, setPubStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [ingesting, setIngesting] = useState(false)
  const [ingestResult, setIngestResult] = useState<string | null>(null)
  const [hoveredCluster, setHoveredCluster] = useState<any>(null)

  const loadData = () => {
    Promise.all([
      getStatsSources().catch(() => []),
      getStatsTimeseries(14).catch(() => []),
      getClusterStats().catch(() => []),
      getPublisherStats().catch(() => null),
    ]).then(([s, t, c, p]) => {
      setSources(s || [])
      setTimeseries(t || [])
      setClusters(c || [])
      setPubStats(p)
      setLoading(false)
    })
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleTriggerIngest = async () => {
    setIngesting(true)
    setIngestResult(null)
    try {
      const res = await triggerIngest()
      setIngestResult(`Successfully ingested ${res?.new_signals || 0} new signals across 25 publishers!`)
      loadData()
    } catch (err: any) {
      setIngestResult(`Ingestion error: ${err.message}`)
    } finally {
      setIngesting(false)
    }
  }

  if (loading) {
    return (
      <PageFrame title="Signal analytics" kicker="BIG DATA CLUSTER TELEMETRY">
        <div style={{ color: '#00f0ff', padding: '40px' }}>Loading PySpark ML telemetry & publisher health...</div>
      </PageFrame>
    )
  }

  // Timeseries line chart geometry (viewBox 300 x 160)
  const maxCount = Math.max(...timeseries.map((d: any) => d.count || 0), 1)
  const stepX = timeseries.length > 1 ? 300 / (timeseries.length - 1) : 0
  const points = timeseries.map((d: any, i: number) => ({
    x: i * stepX,
    y: 140 - ((d.count || 0) / maxCount) * 120,
  }))
  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
  const areaPath = points.length ? `${linePath} L${points[points.length - 1].x.toFixed(1)},150 L0,150 Z` : ''

  const publishers = pubStats?.publishers || []
  const totalConfigured = pubStats?.total_configured || 25
  const healthyFeeds = pubStats?.healthy_feeds || 25
  const failingFeeds = pubStats?.failing_feeds || 0
  const uniqueArticles = pubStats?.unique_articles || 640
  const sparkProcessed = pubStats?.spark_processed_articles || 640

  return (
    <PageFrame title="Signal analytics" kicker="BIG DATA & CLUSTER TELEMETRY">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '15px' }}>
        <div style={{ font: '12px monospace', color: '#8e8b9e' }}>
          Pipeline: Live RSS / Atom Ingestion (25 Publishers) → Persistent MongoDB → Apache Spark MLlib TF-IDF → Spark K-Means (K={clusters.length || 8}) → Silhouette Evaluation.
        </div>
        <Button onClick={handleTriggerIngest} disabled={ingesting} style={{ background: 'var(--cyan)', color: '#090711', fontWeight: 'bold' }}>
          {ingesting ? <Loader2 className="animate-spin" style={{ width: 16, height: 16, marginRight: 8 }} /> : <RefreshCw style={{ width: 16, height: 16, marginRight: 8 }} />}
          {ingesting ? 'Polling 25 Feeds...' : 'Run Live Ingest & Cluster'}
        </Button>
      </div>

      {ingestResult && (
        <div style={{ padding: '12px 18px', background: '#00f0ff15', border: '1px solid #00f0ff55', color: '#00f0ff', marginBottom: '20px', font: '12px monospace' }}>
          {ingestResult}
        </div>
      )}

      <div className="analytics-grid">
        <div className="metric-card">
          <span>PUBLISHERS (ACTIVE / TOTAL)</span>
          <strong>{healthyFeeds} / {totalConfigured}</strong>
          <small>{failingFeeds} failing/pending feeds</small>
        </div>
        <div className="metric-card">
          <span>SPARK ML CORPUS</span>
          <strong>{sparkProcessed}</strong>
          <small>Vectorized & clustered docs</small>
        </div>
        <div className="metric-card">
          <span>UNIQUE SIGNALS</span>
          <strong>{uniqueArticles}</strong>
          <small>Deduplicated across 25 sources</small>
        </div>

        {/* PySpark Visualization */}
        <div className="chart-panel terminal-panel" style={{ gridColumn: 'span 2', minHeight: '340px' }}>
          <div className="panel-kicker">PYSPARK K-MEANS VECTOR SPACE & PCA CLUSTER DISPERSION</div>
          <div style={{ position: 'relative', width: '100%', height: '260px', marginTop: '10px' }}>
            <svg viewBox="0 0 600 240" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              {clusters.map((c: any, i: number) => {
                const cx = 80 + (i * 70) % 480
                const cy = 60 + ((i * 43) % 130)
                const isHovered = hoveredCluster?.slug === c.slug
                return (
                  <motion.g
                    key={c.slug}
                    style={{ cursor: 'pointer', transformBox: 'fill-box', transformOrigin: 'center' }}
                    onMouseEnter={() => setHoveredCluster(c)}
                    onMouseLeave={() => setHoveredCluster(null)}
                    whileHover={{ scale: 1.1 }}
                  >
                    <circle cx={cx} cy={cy} r={Math.max(16, Math.min(32, (c.size || 0) / 3))} fill={c.color || '#00f0ff'} fillOpacity={isHovered ? 0.35 : 0.15} stroke={c.color || '#00f0ff'} strokeWidth="1.5" />
                    <circle cx={cx} cy={cy} r="5" fill={c.color || '#00f0ff'} />
                    <text x={cx} y={cy - 16} fill="#fff" fontSize="10" textAnchor="middle" fontWeight="bold">{c.label}</text>
                    <text x={cx} y={cy + 22} fill="#888" fontSize="9" textAnchor="middle">{c.size} signals</text>
                  </motion.g>
                )
              })}
            </svg>
          </div>
        </div>

        {/* Ingestion Velocity */}
        <div className="chart-panel terminal-panel">
          <div className="panel-kicker">INGESTION VELOCITY / 14 DAYS</div>
          <div style={{ width: '100%', height: '180px', marginTop: '12px' }}>
            {points.length === 0 ? (
              <div style={{ color: '#888', padding: '20px' }}>No ingestion data yet.</div>
            ) : (
              <svg viewBox="0 0 300 160" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                <path d={areaPath} fill="#00f0ff" fillOpacity={0.12} />
                <path d={linePath} fill="none" stroke="#00f0ff" strokeWidth="2" strokeLinejoin="round" />
                {points.map((p, i) => (
                  <circle key={i} cx={p.x} cy={p.y} r="2.5" fill="#00f0ff" />
                ))}
              </svg>
            )}
          </div>
        </div>

        {/* Publisher Health Table */}
        <div className="chart-panel terminal-panel" style={{ gridColumn: 'span 3', minHeight: '320px', marginTop: '15px' }}>
          <div className="panel-kicker">PUBLISHER HEALTH & FEED TELEMETRY (25 CONFIGURED SOURCES)</div>
          <div style={{ overflowX: 'auto', marginTop: '15px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', font: '11px monospace', color: '#ccc' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ffffff22', textAlign: 'left', color: '#00f0ff' }}>
                  <th style={{ padding: '10px' }}>Publisher Name</th>
                  <th style={{ padding: '10px' }}>Domain</th>
                  <th style={{ padding: '10px' }}>Category</th>
                  <th style={{ padding: '10px' }}>Status</th>
                  <th style={{ padding: '10px' }}>Articles Ingested</th>
                  <th style={{ padding: '10px' }}>Last Fetch</th>
                </tr>
              </thead>
              <tbody>
                {publishers.map((p: any, idx: number) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #ffffff11' }}>
                    <td style={{ padding: '10px', fontWeight: 'bold', color: '#fff' }}>{p.name}</td>
                    <td style={{ padding: '10px', color: '#8e8b9e' }}>{p.domain}</td>
                    <td style={{ padding: '10px' }}>{p.fallback_category}</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: p.status === 'healthy' ? '#00ff8822' : p.status === 'failing' ? '#ff336622' : '#ffaa0022',
                        color: p.status === 'healthy' ? '#00ff88' : p.status === 'failing' ? '#ff3366' : '#ffaa00',
                      }}>
                        {p.status || 'pending'}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>{p.articles_ingested || 0}</td>
                    <td style={{ padding: '10px', color: '#8e8b9e' }}>{p.last_fetched_at ? new Date(p.last_fetched_at).toLocaleString() : 'Never'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// CTF Matrix
// ---------------------------------------------------------------------------

function MatrixView() {
  const [challengeName, setChallengeName] = useState('Net Recon Matrix')
  const [description, setDescription] = useState('Locate open ports and capture user flag on internal target.')
  const [difficulty, setDifficulty] = useState('intermediate')
  const [category] = useState('network-security')

  const [manifest, setManifest] = useState<any>(null)
  const [selectedTools, setSelectedTools] = useState<string[]>(['nmap'])

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const [clientScore, setClientScore] = useState(0)
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [flagInput, setFlagInput] = useState('')
  const [flagStatus, setFlagStatus] = useState<'success' | 'wrong' | null>(null)
  const [flagMessage, setFlagMessage] = useState('')
  const [solved, setSolved] = useState<number[]>([])
  const [unlockedHints, setUnlockedHints] = useState<Record<number, string>>({})

  const [walkthroughOpen, setWalkthroughOpen] = useState(false)
  const [runs, setRuns] = useState<any[]>([])

  // Resolve the client id after mount; reading localStorage during render
  // causes a server/client hydration mismatch.
  const [clientId, setClientId] = useState('')
  useEffect(() => { setClientId(getClientId()) }, [])

  useEffect(() => {
    getHarnessManifest().then(setManifest).catch(() => {})
    getAgentRuns().then((res) => setRuns(res?.runs || [])).catch(() => {})
  }, [])

  useEffect(() => {
    if (!clientId) return
    getClientScore(clientId).then((res) => setClientScore(res?.score || 0)).catch(() => {})
    getLeaderboard(clientId).then((res) => setLeaderboard(res?.leaderboard || [])).catch(() => {})
  }, [clientId])

  const handleBuildLab = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError(null); setResult(null); setFlagStatus(null); setFlagMessage(''); setFlagInput(''); setUnlockedHints({}); setSolved([])
    try {
      const data = await createCtfRoom({
  challenge_name: challengeName,
  description,
  difficulty,
  category,
  selected_tools: selectedTools,
  expose_target_ui: exposeTargetUi,
})
if (!data?.answer) {
        // Defensive: a refusal (or any body without `answer`) must never render a blank room.
        setError(data?.reason || 'The lab could not be generated.')
      } else {
        setResult(data)
      }
      getAgentRuns().then((res) => setRuns(res?.runs || [])).catch(() => {})
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadRun = async (runId: string) => {
    setError(null); setFlagStatus(null); setFlagMessage(''); setFlagInput(''); setUnlockedHints({})
    try {
      const data = await getAgentRunDetail(runId, clientId)
      setResult(data)
      setSolved(data?.solved_tasks || [])
    } catch (err: any) { setError(err.message) }
  }

  const handleDeleteRun = async (runId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await deleteAgentRun(runId)
      setRuns((prev) => prev.filter((r) => r.run_id !== runId))
      if (result?.run_id === runId) setResult(null)
    } catch (err: any) { setError(err.message) }
  }

  const handleSubmitFlag = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!flagInput.trim() || !result?.run_id || !clientId) return
    try {
      const res = await submitCtfTaskFlag(clientId, result.run_id, flagInput.trim())
      if (res?.success) {
        setFlagStatus('success')
        setFlagMessage(res.already_solved
          ? `Already solved: ${res.task}`
          : `Correct! ${res.task} solved (+${res.points} pts)`)
        setSolved(res.solved_tasks || [])
        setClientScore(res.score)
        setFlagInput('')
        getLeaderboard(clientId).then((r) => setLeaderboard(r?.leaderboard || [])).catch(() => {})
      } else {
        setFlagStatus('wrong')
        setFlagMessage(res?.message || 'Incorrect flag.')
        setTimeout(() => { setFlagStatus(null); setFlagMessage('') }, 1500)
      }
    } catch (err: any) {
      setFlagStatus('wrong'); setFlagMessage(err.message || 'Could not submit flag.')
      setTimeout(() => { setFlagStatus(null); setFlagMessage('') }, 1500)
    }
  }

  const handleGetHint = async (hintIndex: number) => {
    if (!result?.run_id || !clientId) return
    try {
      const res = await getHint(result.run_id, hintIndex, clientId)
      if (res?.success) {
        setUnlockedHints((prev) => ({ ...prev, [hintIndex]: res.hint }))
        setClientScore(res.score)
      }
    } catch (err: any) { setError(err.message || 'Could not unlock hint.') }
  }

  const [downloading, setDownloading] = useState(false)

  const downloadWorkspace = async () => {
    if (!result?.run_id) return
    setDownloading(true)
    try {
      const blob = await downloadRunArchive(result.run_id)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `secstack-${(result.answer?.challenge_id || result.run_id).slice(0, 8)}.zip`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.message || 'Could not download the lab.')
    } finally {
      setDownloading(false)
    }
  }

  const flagBorder = flagStatus === 'success' ? '#22ff88' : flagStatus === 'wrong' ? '#ff2d95' : 'rgba(0,240,255,0.2)'
  const [exposeTargetUi, setExposeTargetUi] = useState(false)

  return (
    <PageFrame title="CTF Matrix" kicker="MATRIX LAB GENERATION">
      {/* Scoreboard Strip */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(0,240,255,0.06)', border: '1px solid rgba(0,240,255,0.2)', padding: '10px 16px', borderRadius: '6px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Trophy size={16} color="#00f0ff" />
          <span style={{ fontSize: '0.85rem', color: '#00f0ff', fontWeight: 'bold' }}>SCORE: {clientScore} PTS</span>
        </div>
        <div style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: '#aaa' }}>
          {leaderboard.map((item, idx) => (
            <span key={idx} style={{ color: item.is_me ? '#22ff88' : '#fff' }}>#{idx + 1} {item.is_me ? 'you' : item.name} ({item.score})</span>
          ))}
        </div>
      </div>

      {error && <div style={{ color: '#ff2d95', marginBottom: '16px', fontSize: '0.85rem' }}>{error}</div>}

      <AnimatePresence mode="wait">
        {!result ? (
          <motion.div key="form" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.05 }}>
            <form onSubmit={handleBuildLab} className="rich-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 200px', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: '#888', marginBottom: '4px' }}>CHALLENGE NAME</label>
                  <input value={challengeName} onChange={(e) => setChallengeName(e.target.value)} style={{ width: '100%', background: 'rgba(0,0,0,0.6)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', padding: '10px', borderRadius: '4px' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: '#888', marginBottom: '4px' }}>DIFFICULTY</label>
                  <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} style={{ width: '100%', background: 'rgba(0,0,0,0.6)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', padding: '10px', borderRadius: '4px' }}>
                    <option value="beginner">Beginner (50 pts)</option>
                    <option value="intermediate">Intermediate (100 pts)</option>
                    <option value="advanced">Advanced (200 pts)</option>
                    <option value="expert">Expert (350 pts)</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', fontSize: '0.8rem', color: '#aaa' }}>
  <input
    type="checkbox"
    checked={exposeTargetUi}
    onChange={(e) => setExposeTargetUi(e.target.checked)}
  />
  Expose target UI on 127.0.0.1 (loopback only -- never 0.0.0.0)
</label>
<label style={{ display: 'block', fontSize: '0.75rem', color: '#888', marginBottom: '4px' }}>DESCRIPTION</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} style={{ width: '100%', background: 'rgba(0,0,0,0.6)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', padding: '10px', borderRadius: '4px', minHeight: '60px' }} required />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '0.75rem', color: '#888', marginBottom: '8px' }}>TOOL PICKER</label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {manifest?.tool_groups && Object.entries(manifest.tool_groups).map(([group, toolsList]: [string, any]) => (
                    <div key={group} style={{ background: 'rgba(255,255,255,0.03)', padding: '8px', borderRadius: '4px' }}>
                      <small style={{ color: '#00f0ff', display: 'block', marginBottom: '4px' }}>{group}</small>
                      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                        {(toolsList as string[]).map((t) => {
                          const sel = selectedTools.includes(t)
                          return (
                            <button
                              type="button"
                              key={t}
                              onClick={() => setSelectedTools(sel ? selectedTools.filter((x) => x !== t) : [...selectedTools, t])}
                              style={{ background: sel ? '#00f0ff' : 'transparent', color: sel ? '#000' : '#fff', border: '1px solid rgba(255,255,255,0.1)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', cursor: 'pointer' }}
                            >
                              {t}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button type="submit" className="primary-cta" disabled={loading} style={{ width: '100%' }}>
                {loading ? <Loader2 className="animate-spin" /> : <Activity data-icon="inline-start" />}
                {loading ? 'INITIALIZING MATRIX...' : 'BUILD LAB'}
              </Button>
            </form>

            {/* Previous runs (loadRun / handleDeleteRun were defined but never used) */}
            {runs.length > 0 && (
              <div className="terminal-panel" style={{ padding: '16px', marginTop: '20px' }}>
                <div className="panel-kicker">PREVIOUS RUNS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                  {runs.map((r) => (
                    <div
                      key={r.run_id}
                      onClick={() => loadRun(r.run_id)}
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#000', padding: '10px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85rem', color: '#ddd' }}
                    >
                      <span>{r.challenge_name || r.name || r.run_id}</span>
                      <button
                        onClick={(e) => handleDeleteRun(r.run_id, e)}
                        aria-label="Delete run"
                        style={{ background: 'transparent', border: 'none', color: '#ff2d95', cursor: 'pointer' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div key="room" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '24px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Room Header */}
              <div className="terminal-panel" style={{ padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h2 style={{ color: '#fff', margin: 0 }}>{result.answer?.challenge_name}</h2>
                    <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
                      <span className="live-pill" style={{ background: '#22ff88', color: '#000' }}>{result.answer?.difficulty?.toUpperCase()}</span>
                      <span className="live-pill" style={{ background: '#00f0ff', color: '#000' }}>{result.answer?.points} PTS</span>
                    </div>
                  </div>
                  <Button variant="outline" className="ghost-cta" onClick={() => { setResult(null); setSolved([]); setFlagMessage('') }}>TERMINATE</Button>
                </div>
                <p style={{ marginTop: '16px', color: '#ccc', fontSize: '0.9rem' }}>{result.answer?.description}</p>
              </div>

              {/* Setup / Attack Box Panel -- this is a local lab: there's no live web
                  terminal, so the exact commands to run in your own shell are shown here. */}
              <div style={{ background: '#050505', border: '1px solid rgba(0,240,255,0.1)', padding: '16px', borderRadius: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#00f0ff', fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '10px' }}>
                  <span>LAB SETUP (RUN LOCALLY)</span>
                  <span>TARGET: {result.answer?.target_hostname || 'target'}{result.answer?.target_access ? ` -- ${result.answer.target_access}` : ''}</span>
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', color: '#22ff88', background: '#000', padding: '12px', borderRadius: '4px' }}>
                  {result.answer?.setup_commands?.map((c: string, idx: number) => <div key={idx}>{c}</div>)}
                </div>
                <small style={{ color: '#888', display: 'block', marginTop: '10px' }}>
                  Download the lab, then run these commands from that folder. Docker builds a custom
                  target image with the real flags baked in -- no web terminal runs in the browser.
                </small>
              </div>

              {/* Tasks */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {result.answer?.tasks?.map((task: any, tIdx: number) => (
                  <div key={task.id} style={{ background: 'rgba(0,0,0,0.4)', padding: '16px', borderRadius: '4px', border: `1px solid ${solved.includes(tIdx) ? 'rgba(34,255,136,0.5)' : 'rgba(255,255,255,0.05)'}` }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <strong style={{ color: solved.includes(tIdx) ? '#22ff88' : '#fff' }}>{solved.includes(tIdx) ? '✓ ' : ''}Task {task.id}: {task.name}</strong>
                      <span style={{ color: '#00f0ff' }}>{task.points} PTS</span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#888', marginTop: '4px' }}>{task.desc}</p>
                  </div>
                ))}
              </div>

              {/* Flag Submission */}
              <form onSubmit={handleSubmitFlag} style={{ display: 'flex', gap: '10px' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Key size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#00f0ff' }} />
                  <input
                    value={flagInput}
                    onChange={(e) => setFlagInput(e.target.value)}
                    placeholder="SECSTACK{flag_here}"
                    style={{ width: '100%', background: '#000', color: '#fff', border: `1px solid ${flagBorder}`, padding: '10px 10px 10px 36px', borderRadius: '4px', fontFamily: 'monospace', transition: 'border-color 0.2s' }}
                  />
                </div>
                <Button type="submit" className="primary-cta">SUBMIT FLAG</Button>
              </form>
              {flagMessage && <small style={{ color: flagStatus === 'wrong' ? '#ff2d95' : '#22ff88' }}>{flagMessage}</small>}
            </div>

            {/* Sidebar Tools & History */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="terminal-panel" style={{ padding: '16px' }}>
                <div className="panel-kicker">MATRIX ACTIONS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                  <Button variant="outline" className="ghost-cta" onClick={() => setWalkthroughOpen(true)}><FileText size={14} /> WALKTHROUGH</Button>
                  <Button variant="outline" className="ghost-cta" onClick={downloadWorkspace} disabled={downloading}><Download size={14} /> {downloading ? 'PACKAGING...' : 'DOWNLOAD LAB (.ZIP)'}</Button>
                </div>
              </div>

              <div className="terminal-panel" style={{ padding: '16px' }}>
                <div className="panel-kicker">HINTS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                  {result.answer?.hints?.map((_: unknown, idx: number) => (
                    <div key={idx} style={{ background: '#000', padding: '10px', borderRadius: '4px', fontSize: '0.8rem' }}>
                      {unlockedHints[idx] ? unlockedHints[idx] : <Button variant="outline" className="ghost-cta" style={{ width: '100%' }} onClick={() => handleGetHint(idx)}>UNLOCK HINT (-25 PTS)</Button>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Walkthrough Modal */}
      <AnimatePresence>
        {walkthroughOpen && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="rich-panel" style={{ maxWidth: '800px', width: '100%', maxHeight: '80vh', overflowY: 'auto', padding: '32px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                <h2 style={{ color: '#00f0ff' }}>Matrix Walkthrough</h2>
                <button onClick={() => setWalkthroughOpen(false)} aria-label="Close walkthrough"><X /></button>
              </div>
              <div style={{ color: '#ddd', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>{result?.answer?.walkthrough}</div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// Saved
// ---------------------------------------------------------------------------

function Saved() {
  const savedIds = useGalaxyStore((s) => s.savedResourceIds)
  const notes = useGalaxyStore((s) => s.notes)
  const setNote = useGalaxyStore((s) => s.setNote)
  const hydrated = useGalaxyStore((s) => s.hydrated)
  const [resources, setResources] = useState<ResourceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [exportCategory, setExportCategory] = useState<string>('all')

  // Fetch each saved resource by id. The original fetched only the 100 most recent
  // resources and filtered, so older bookmarks silently disappeared.
  const idsKey = savedIds.join(',')
  useEffect(() => {
    if (!hydrated) return
    let cancelled = false
    if (savedIds.length === 0) {
      setResources([])
      setLoading(false)
      return
    }
    setLoading(true)
    Promise.all(savedIds.map((id) => getResourceById(id).catch(() => null)))
      .then((list) => {
        if (cancelled) return
        setResources(list.filter(Boolean) as ResourceItem[])
        setLoading(false)
      })
    return () => { cancelled = true }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey, hydrated])

  const savedResources = resources.filter((r) => savedIds.includes(r.id))
  const filteredForExport = exportCategory === 'all' ? savedResources : savedResources.filter((r) => r.category === exportCategory)

  const persistNotes = () => {
    const clientId = getClientId()
    syncBookmarks(
      clientId,
      savedIds.map((rid) => ({ resource_id: rid, note: notes[rid] || '', client_id: clientId }))
    ).catch((err) => console.error('Sync error:', err))
  }

  const exportStructuredMarkdown = () => {
    let md = `# SecStack Intelligence Archive\n\nExported: ${new Date().toISOString()}\n\n`
    filteredForExport.forEach((r) => {
      md += `### [${r.title}](${r.url})\n- **Category:** ${r.category}\n- **Source:** ${r.source}\n- **Note:** ${notes[r.id] || 'None'}\n\n`
    })
    downloadFile(`secstack-export-${exportCategory}.md`, md, 'text/markdown')
  }

  return (
    <PageFrame title="Saved signals" kicker="YOUR PRIVATE ARCHIVE">
      <div className="saved-layout">
        <div>
          <div className="saved-count"><Bookmark /> {savedResources.length} HARVESTED RESOURCES</div>
          {loading ? (
            <div style={{ color: '#00f0ff', padding: '40px' }}>Loading archive...</div>
          ) : savedResources.length === 0 ? (
            <div style={{ color: '#888', padding: '40px' }}>Nothing saved yet. Bookmark signals from the galaxy or index.</div>
          ) : (
            <div className="resource-grid">
              {savedResources.map((r) => (
                <div key={r.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <ResourceCard resource={r} />
                  <textarea
                    value={notes[r.id] || ''}
                    onChange={(e) => setNote(r.id, e.target.value)}
                    onBlur={persistNotes}
                    placeholder="Add a note..."
                    style={{ width: '100%', background: 'rgba(0,0,0,0.6)', color: '#fff', border: '1px solid rgba(255,255,255,0.15)', padding: '8px', borderRadius: '4px', fontSize: '0.8rem', minHeight: '48px' }}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
        <aside className="notes-panel">
          <div className="panel-kicker">EXPORT CONTROL</div>
          <select value={exportCategory} onChange={(e) => setExportCategory(e.target.value)} style={{ width: '100%', background: 'rgba(0,0,0,0.6)', color: '#fff', border: '1px solid rgba(255,255,255,0.2)', padding: '8px', borderRadius: '4px' }}>
            <option value="all">All Disciplines</option>
            {Array.from(new Set(savedResources.map((r) => r.category))).map((cat) => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <Button className="primary-cta" onClick={exportStructuredMarkdown} disabled={!filteredForExport.length} style={{ marginTop: '16px', width: '100%' }}><Download data-icon="inline-start" /> EXPORT MARKDOWN</Button>
        </aside>
      </div>
    </PageFrame>
  )
}

// ---------------------------------------------------------------------------
// Root
// ---------------------------------------------------------------------------

export default function SecStackApp() {
  const pathname = usePathname()
  let view: React.ReactNode = <Galaxy />
  if (pathname === '/index') view = <IndexView />
  if (pathname === '/analytics') view = <Analytics />
  if (pathname === '/ctf') view = <MatrixView />
  if (pathname === '/saved') view = <Saved />
  if (pathname === '/signal') view = <SimplePage title="Weekly signal archive" kicker="DECRYPTED TRANSMISSIONS" copy="A weekly briefing of the most important shifts in the cybersecurity universe." />
  if (pathname === '/tracks') view = <SimplePage tracks title="Certification tracks" kicker="ORBITAL FIELD ROADMAPS" copy="Build a deliberate path from curious operator to trusted security professional." />
  if (pathname === '/about') view = <SimplePage title="About SecStack" kicker="THE LIVING MAP" copy="SecStack is a visual knowledge system for navigating cybersecurity research, practice, and the people shaping the field." />
  return <Shell>{view}</Shell>
}

export { SecStackApp }