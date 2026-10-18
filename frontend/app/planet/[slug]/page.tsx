import { PlanetDetail } from '@/components/secstack-app'

export default async function PlanetPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  return <PlanetDetail slug={slug} />
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  return { title: `${slug.replaceAll('-', ' ')} // SecStack`, description: 'JARVIS planetary command center for cybersecurity intelligence.' }
}

export function generateStaticParams() {
  return ['network-security', 'web-security', 'cloud-security', 'cryptography', 'threat-intel', 'career-guides'].map((slug) => ({ slug }))
}
