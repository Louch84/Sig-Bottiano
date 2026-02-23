"""
Deep Research Agent
Autonomous web research using free search
Combines multiple sources into comprehensive report
"""

import asyncio
import json
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class ResearchSource:
    """Represents a research source"""
    url: str
    title: str
    content: str
    relevance_score: float
    date: Optional[str] = None

@dataclass
class ResearchReport:
    """Comprehensive research report"""
    query: str
    summary: str
    key_findings: List[str]
    sources: List[ResearchSource]
    bullish_case: str
    bearish_case: str
    trading_thesis: str
    risk_factors: List[str]
    confidence: float
    timestamp: str


class DeepResearchAgent:
    """
    Autonomous deep research agent.
    Uses free web search (Brave API) with rate limiting.
    """
    
    def __init__(self, brave_api_key: Optional[str] = None):
        self.brave_key = brave_api_key
        self.max_sources = 15
        self.search_count = 0
        self.max_searches_per_run = 10  # Rate limit
    
    async def research_stock(self, symbol: str, specific_aspect: str = None) -> Optional[ResearchReport]:
        """
        Deep research on a stock
        
        Args:
            symbol: Stock ticker
            specific_aspect: E.g., "short interest", "earnings", "catalysts"
        """
        print(f"🔬 Deep Research: {symbol}")
        print(f"   Query: {specific_aspect or 'Comprehensive analysis'}")
        print()
        
        # Build search queries
        queries = self._build_queries(symbol, specific_aspect)
        
        # Execute searches
        all_sources = []
        for query in queries[:self.max_searches_per_run]:
            sources = await self._search(query)
            all_sources.extend(sources)
            await asyncio.sleep(1)  # Rate limiting
        
        if not all_sources:
            return None
        
        # Deduplicate and rank
        unique_sources = self._deduplicate_sources(all_sources)
        ranked_sources = self._rank_sources(unique_sources, symbol)
        
        # Take top sources
        top_sources = ranked_sources[:self.max_sources]
        
        # Generate report
        report = self._generate_report(symbol, specific_aspect, top_sources)
        
        return report
    
    def _build_queries(self, symbol: str, aspect: str = None) -> List[str]:
        """Build search queries for comprehensive research"""
        
        if aspect:
            return [
                f"{symbol} {aspect} 2026",
                f"{symbol} {aspect} analysis",
                f"{symbol} stock {aspect}"
            ]
        
        return [
            f"{symbol} stock analysis 2026",
            f"{symbol} short interest borrow rate",
            f"{symbol} options flow unusual activity",
            f"{symbol} earnings catalyst upcoming",
            f"{symbol} reddit wallstreetbets sentiment",
            f"{symbol} institutional ownership holdings",
            f"{symbol} price target analyst rating"
        ]
    
    async def _search(self, query: str) -> List[ResearchSource]:
        """Execute search using Brave API"""
        
        if not self.brave_key:
            # Fallback: return empty (would need API key for real search)
            return []
        
        try:
            import aiohttp
            
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_key
            }
            params = {
                "q": query,
                "count": 5,
                "freshness": "pw"  # Past week
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        sources = []
                        for result in data.get('web', {}).get('results', []):
                            source = ResearchSource(
                                url=result.get('url', ''),
                                title=result.get('title', ''),
                                content=result.get('description', '')[:500],
                                relevance_score=0.0,
                                date=result.get('age', None)
                            )
                            sources.append(source)
                        
                        self.search_count += 1
                        return sources
                    else:
                        return []
                        
        except Exception as e:
            print(f"   ⚠️  Search error: {e}")
            return []
    
    def _deduplicate_sources(self, sources: List[ResearchSource]) -> List[ResearchSource]:
        """Remove duplicate sources by URL"""
        seen = set()
        unique = []
        
        for source in sources:
            url_key = source.url.split('?')[0]  # Remove query params
            if url_key not in seen:
                seen.add(url_key)
                unique.append(source)
        
        return unique
    
    def _rank_sources(self, sources: List[ResearchSource], symbol: str) -> List[ResearchSource]:
        """Rank sources by relevance"""
        
        for source in sources:
            score = 0.0
            text = (source.title + " " + source.content).lower()
            
            # Symbol mention
            if symbol.lower() in text:
                score += 0.3
            
            # Financial keywords
            financial_terms = ['stock', 'trading', 'price', 'earnings', 'revenue', 'short', 'options']
            for term in financial_terms:
                if term in text:
                    score += 0.1
            
            # Quality indicators
            if 'analysis' in text or 'report' in text:
                score += 0.2
            
            if 'breaking' in text or 'news' in text:
                score += 0.15
            
            source.relevance_score = min(1.0, score)
        
        # Sort by relevance
        return sorted(sources, key=lambda x: x.relevance_score, reverse=True)
    
    def _generate_report(self, symbol: str, aspect: str, sources: List[ResearchSource]) -> ResearchReport:
        """Generate comprehensive research report"""
        
        # Extract key information from sources
        all_text = " ".join([s.title + " " + s.content for s in sources])
        
        # Sentiment analysis (simple keyword-based)
        bullish_keywords = ['buy', 'bullish', 'growth', 'upside', 'target', 'strong', 'beat']
        bearish_keywords = ['sell', 'bearish', 'decline', 'downside', 'weak', 'miss', 'short']
        
        bullish_count = sum(1 for word in bullish_keywords if word in all_text.lower())
        bearish_count = sum(1 for word in bearish_keywords if word in all_text.lower())
        
        total = bullish_count + bearish_count
        if total > 0:
            sentiment_score = bullish_count / total
        else:
            sentiment_score = 0.5
        
        # Extract key findings
        findings = self._extract_findings(sources, symbol)
        
        # Generate trading thesis
        if sentiment_score > 0.6:
            thesis = f"BULLISH: {symbol} shows positive sentiment with {bullish_count} bullish vs {bearish_count} bearish indicators."
        elif sentiment_score < 0.4:
            thesis = f"BEARISH: {symbol} shows negative sentiment with {bearish_count} bearish vs {bullish_count} bullish indicators."
        else:
            thesis = f"NEUTRAL: {symbol} shows mixed sentiment. Wait for clearer direction."
        
        # Risk factors
        risks = self._identify_risks(all_text)
        
        return ResearchReport(
            query=f"{symbol} {aspect or 'comprehensive analysis'}",
            summary=self._generate_summary(sources, symbol),
            key_findings=findings,
            sources=sources,
            bullish_case=f"Positive indicators: {bullish_count} bullish signals detected" if bullish_count > 0 else "Limited bullish data",
            bearish_case=f"Negative indicators: {bearish_count} bearish signals detected" if bearish_count > 0 else "Limited bearish data",
            trading_thesis=thesis,
            risk_factors=risks,
            confidence=sentiment_score,
            timestamp=datetime.now().isoformat()
        )
    
    def _extract_findings(self, sources: List[ResearchSource], symbol: str) -> List[str]:
        """Extract key findings from sources"""
        findings = []
        
        for source in sources[:5]:  # Top 5 sources
            # Extract key sentences
            text = source.content
            sentences = text.split('.')
            
            for sentence in sentences:
                sentence = sentence.strip()
                # Look for sentences with numbers or key metrics
                if any(char.isdigit() for char in sentence) and len(sentence) > 20:
                    findings.append(sentence[:150])  # Truncate
                    break  # One finding per source
        
        return findings[:5]  # Max 5 findings
    
    def _identify_risks(self, text: str) -> List[str]:
        """Identify risk factors in text"""
        risks = []
        
        risk_keywords = {
            'volatility': 'High volatility risk',
            'earnings': 'Earnings announcement risk',
            'debt': 'High debt levels',
            'competition': 'Competitive pressure',
            'regulation': 'Regulatory risk',
            'short': 'Short squeeze potential' if 'short squeeze' in text.lower() else 'Short interest risk'
        }
        
        for keyword, risk in risk_keywords.items():
            if keyword in text.lower():
                risks.append(risk)
        
        return risks[:3]  # Top 3 risks
    
    def _generate_summary(self, sources: List[ResearchSource], symbol: str) -> str:
        """Generate executive summary"""
        num_sources = len(sources)
        top_source = sources[0] if sources else None
        
        if top_source:
            return f"Analysis of {symbol} based on {num_sources} sources. Top source: {top_source.title}. Key themes include market sentiment, trading activity, and upcoming catalysts."
        else:
            return f"Limited data available for {symbol}. Recommend additional research."


class ResearchReportFormatter:
    """Format research reports for display"""
    
    @staticmethod
    def format_report(report: ResearchReport) -> str:
        """Format report as readable text"""
        lines = []
        
        lines.append("="*70)
        lines.append("🔬 DEEP RESEARCH REPORT")
        lines.append("="*70)
        lines.append(f"\nQuery: {report.query}")
        lines.append(f"Generated: {report.timestamp}")
        lines.append(f"Sources: {len(report.sources)}")
        lines.append(f"Confidence: {report.confidence:.0%}")
        lines.append()
        
        lines.append("📊 SUMMARY")
        lines.append(report.summary)
        lines.append()
        
        lines.append("🎯 KEY FINDINGS")
        for i, finding in enumerate(report.key_findings, 1):
            lines.append(f"  {i}. {finding}")
        lines.append()
        
        lines.append("📈 BULLISH CASE")
        lines.append(f"  {report.bullish_case}")
        lines.append()
        
        lines.append("📉 BEARISH CASE")
        lines.append(f"  {report.bearish_case}")
        lines.append()
        
        lines.append("💡 TRADING THESIS")
        lines.append(f"  {report.trading_thesis}")
        lines.append()
        
        lines.append("⚠️  RISK FACTORS")
        for risk in report.risk_factors:
            lines.append(f"  • {risk}")
        lines.append()
        
        lines.append("📚 SOURCES")
        for i, source in enumerate(report.sources[:5], 1):
            lines.append(f"  {i}. {source.title}")
            lines.append(f"     URL: {source.url}")
            lines.append(f"     Relevance: {source.relevance_score:.0%}")
        lines.append()
        
        lines.append("="*70)
        
        return "\n".join(lines)


# Demo
async def demo():
    """Demonstrate deep research"""
    print("="*70)
    print("🔬 DEEP RESEARCH AGENT DEMO")
    print("="*70)
    print()
    
    # Note: Requires Brave API key for actual search
    # Without key, will return empty results
    
    agent = DeepResearchAgent(
        brave_api_key="BSAAOviRBRs0OehyYS__2pZ0zhq_-B_"
    )
    
    report = await agent.research_stock("AMC", "short interest")
    
    if report:
        formatter = ResearchReportFormatter()
        print(formatter.format_report(report))
    else:
        print("❌ Research failed - check API key")

if __name__ == "__main__":
    asyncio.run(demo())
