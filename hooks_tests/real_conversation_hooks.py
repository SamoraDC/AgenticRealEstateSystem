#!/usr/bin/env python3
"""
Sistema de Hooks de Conversa REAL - Real Estate Assistant
Integrado com sistema agêntico real para monitoramento em produção
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from app.orchestration.swarm import SwarmOrchestrator
from app.utils.logging import get_logger, log_agent_action, log_api_call, log_error
from config.settings import get_settings

class RealConversationPhase(Enum):
    """Fases da conversa no sistema real"""
    GREETING = "greeting"
    SEARCH_CRITERIA = "search_criteria"
    PROPERTY_DETAILS = "property_details"
    SCHEDULING = "scheduling"
    CLOSING = "closing"
    ERROR_HANDLING = "error_handling"

class RealAgentType(Enum):
    """Tipos de agentes no sistema real"""
    SEARCH_AGENT = "search_agent"
    PROPERTY_AGENT = "property_agent"
    SCHEDULING_AGENT = "scheduling_agent"

@dataclass
class RealConversationEvent:
    """Evento de conversa capturado do sistema real"""
    timestamp: datetime
    agent_type: RealAgentType
    phase: RealConversationPhase
    user_input: str
    agent_response: str
    response_time: float
    session_id: str
    success: bool
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None

@dataclass
class RealConversationFlow:
    """Fluxo completo de conversa no sistema real"""
    session_id: str
    user_profile: str
    events: List[RealConversationEvent] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    agent_transitions: List[Dict[str, Any]] = field(default_factory=list)
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    system_performance: Dict[str, Any] = field(default_factory=dict)

class RealConversationHook:
    """Hook para capturar eventos de conversa do sistema real"""
    
    def __init__(self, name: str, trigger_condition: Callable[[RealConversationEvent], bool], 
                 priority: int = 1):
        self.name = name
        self.trigger_condition = trigger_condition
        self.priority = priority
        self.captured_events: List[RealConversationEvent] = []
        self.is_active = True
        self.logger = get_logger(f"hook_{name}")
    
    def capture(self, event: RealConversationEvent) -> bool:
        """Captura evento se a condição for atendida"""
        if self.is_active and self.trigger_condition(event):
            self.captured_events.append(event)
            self.logger.info(f"📎 Hook '{self.name}' capturou evento: {event.user_input[:50]}...")
            
            # Log da captura
            log_agent_action(
                agent_name="conversation_hook",
                action="event_captured",
                details={
                    "hook_name": self.name,
                    "event_type": f"{event.agent_type.value}_{event.phase.value}",
                    "success": event.success,
                    "response_time": event.response_time
                }
            )
            return True
        return False
    
    def get_captured_events(self) -> List[RealConversationEvent]:
        """Retorna eventos capturados"""
        return self.captured_events.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos eventos capturados"""
        if not self.captured_events:
            return {"total_events": 0}
        
        return {
            "total_events": len(self.captured_events),
            "success_rate": sum(1 for e in self.captured_events if e.success) / len(self.captured_events) * 100,
            "average_response_time": sum(e.response_time for e in self.captured_events) / len(self.captured_events),
            "agents_involved": list(set(e.agent_type.value for e in self.captured_events)),
            "phases_covered": list(set(e.phase.value for e in self.captured_events)),
            "time_range": {
                "start": min(e.timestamp for e in self.captured_events),
                "end": max(e.timestamp for e in self.captured_events)
            }
        }
    
    def reset(self):
        """Reseta eventos capturados"""
        self.captured_events.clear()
        self.logger.info(f"🔄 Hook '{self.name}' resetado")

class RealConversationAnalyzer:
    """Analisador de padrões de conversa do sistema real"""
    
    def __init__(self):
        self.flows: List[RealConversationFlow] = []
        self.hooks: List[RealConversationHook] = []
        self.logger = get_logger("conversation_analyzer")
        self.swarm = SwarmOrchestrator()
        self.active_sessions: Dict[str, RealConversationFlow] = {}
    
    def create_production_hooks(self) -> List[RealConversationHook]:
        """Cria hooks específicos para sistema de produção"""
        hooks = [
            # Hook crítico: Transições de agente
            RealConversationHook(
                "agent_transitions",
                lambda event: self._detect_agent_transition(event),
                priority=1
            ),
            
            # Hook crítico: Respostas lentas (>5s)
            RealConversationHook(
                "slow_responses",
                lambda event: event.response_time > 5.0,
                priority=1
            ),
            
            # Hook de negócio: Discussões de preço
            RealConversationHook(
                "price_discussions",
                lambda event: any(word in event.user_input.lower() or word in event.agent_response.lower() 
                                for word in ["price", "cost", "rent", "budget", "$", "expensive", "cheap"]),
                priority=2
            ),
            
            # Hook de negócio: Pedidos de agendamento
            RealConversationHook(
                "scheduling_requests",
                lambda event: any(word in event.user_input.lower() or word in event.agent_response.lower() 
                                for word in ["schedule", "appointment", "viewing", "visit", "tour", "when", "time"]),
                priority=2
            ),
            
            # Hook crítico: Erros e problemas
            RealConversationHook(
                "error_responses",
                lambda event: not event.success or any(word in event.agent_response.lower() 
                                for word in ["error", "sorry", "problem", "issue", "unavailable", "failed"]),
                priority=1
            ),
            
            # Hook de qualidade: Respostas muito curtas (<50 chars)
            RealConversationHook(
                "short_responses",
                lambda event: len(event.agent_response.strip()) < 50,
                priority=2
            ),
            
            # Hook de engajamento: Perguntas sobre propriedades específicas
            RealConversationHook(
                "property_inquiries",
                lambda event: any(word in event.user_input.lower() 
                                for word in ["property", "apartment", "house", "bedroom", "bathroom", "sqft", "square"]),
                priority=2
            ),
            
            # Hook de sistema: Fallbacks para Ollama
            RealConversationHook(
                "ollama_fallbacks",
                lambda event: "ollama" in event.metadata.get("model_used", "").lower(),
                priority=1
            ),
            
            # Hook de performance: Respostas muito rápidas (<0.5s) - possível cache
            RealConversationHook(
                "fast_responses",
                lambda event: event.response_time < 0.5,
                priority=3
            ),
            
            # Hook de experiência: Múltiplas perguntas na mesma sessão
            RealConversationHook(
                "engaged_users",
                lambda event: self._detect_engaged_user(event),
                priority=3
            )
        ]
        
        for hook in hooks:
            self.add_hook(hook)
        
        self.logger.info(f"✅ Criados {len(hooks)} hooks de produção")
        return hooks
    
    def _detect_agent_transition(self, event: RealConversationEvent) -> bool:
        """Detecta transição entre agentes"""
        session_flow = self.active_sessions.get(event.session_id)
        if session_flow and len(session_flow.events) > 0:
            last_agent = session_flow.events[-1].agent_type
            return last_agent != event.agent_type
        return False
    
    def _detect_engaged_user(self, event: RealConversationEvent) -> bool:
        """Detecta usuário engajado (múltiplas interações)"""
        session_flow = self.active_sessions.get(event.session_id)
        if session_flow:
            return len(session_flow.events) >= 3
        return False
    
    def add_hook(self, hook: RealConversationHook):
        """Adiciona hook de captura"""
        self.hooks.append(hook)
        # Ordenar por prioridade
        self.hooks.sort(key=lambda h: h.priority)
    
    def start_conversation_monitoring(self, session_id: str, user_profile: str = "unknown") -> RealConversationFlow:
        """Inicia monitoramento de conversa"""
        flow = RealConversationFlow(
            session_id=session_id,
            user_profile=user_profile,
            start_time=datetime.now()
        )
        self.active_sessions[session_id] = flow
        self.logger.info(f"🎬 Iniciando monitoramento da sessão: {session_id}")
        return flow
    
    def add_real_event(self, event: RealConversationEvent):
        """Adiciona evento de conversa real"""
        # Garantir que a sessão existe
        if event.session_id not in self.active_sessions:
            self.start_conversation_monitoring(event.session_id)
        
        flow = self.active_sessions[event.session_id]
        flow.events.append(event)
        
        # Detectar transições de agente
        if len(flow.events) > 1:
            previous_agent = flow.events[-2].agent_type
            current_agent = event.agent_type
            
            if previous_agent != current_agent:
                transition = {
                    "from": previous_agent.value,
                    "to": current_agent.value,
                    "timestamp": event.timestamp,
                    "trigger": event.user_input,
                    "success": event.success
                }
                flow.agent_transitions.append(transition)
                
                self.logger.info(f"🔄 Transição detectada: {previous_agent.value} → {current_agent.value}")
        
        # Aplicar hooks
        hooks_triggered = 0
        for hook in self.hooks:
            if hook.capture(event):
                hooks_triggered += 1
        
        if hooks_triggered > 0:
            self.logger.info(f"📎 {hooks_triggered} hooks acionados para evento")
        
        # Log do evento
        log_agent_action(
            agent_name="conversation_monitor",
            action="event_processed",
            details={
                "session_id": event.session_id,
                "agent_type": event.agent_type.value,
                "phase": event.phase.value,
                "success": event.success,
                "response_time": event.response_time,
                "hooks_triggered": hooks_triggered
            }
        )
    
    def end_conversation_monitoring(self, session_id: str) -> Optional[RealConversationFlow]:
        """Finaliza monitoramento de conversa"""
        if session_id not in self.active_sessions:
            return None
        
        flow = self.active_sessions[session_id]
        flow.end_time = datetime.now()
        flow.total_duration = (flow.end_time - flow.start_time).total_seconds()
        
        # Calcular métricas de sucesso
        flow.success_metrics = self._calculate_real_success_metrics(flow)
        flow.system_performance = self._calculate_system_performance(flow)
        
        # Mover para histórico
        self.flows.append(flow)
        del self.active_sessions[session_id]
        
        self.logger.info(f"🏁 Finalizando monitoramento da sessão: {session_id}")
        self.logger.info(f"   Duração: {flow.total_duration:.2f}s, Eventos: {len(flow.events)}")
        
        return flow
    
    def _calculate_real_success_metrics(self, flow: RealConversationFlow) -> Dict[str, Any]:
        """Calcula métricas de sucesso para sistema real"""
        if not flow.events:
            return {"error": "No events to analyze"}
        
        successful_events = [e for e in flow.events if e.success]
        
        metrics = {
            "total_interactions": len(flow.events),
            "successful_interactions": len(successful_events),
            "success_rate": len(successful_events) / len(flow.events) * 100,
            "agent_transitions": len(flow.agent_transitions),
            "average_response_time": sum(e.response_time for e in flow.events) / len(flow.events),
            "phases_covered": len(set(e.phase for e in flow.events)),
            "agents_used": len(set(e.agent_type for e in flow.events)),
            "conversation_quality": "unknown",
            "user_engagement": "unknown"
        }
        
        # Determinar qualidade da conversa
        if metrics["success_rate"] >= 95 and metrics["average_response_time"] < 3.0:
            metrics["conversation_quality"] = "excellent"
        elif metrics["success_rate"] >= 85 and metrics["average_response_time"] < 5.0:
            metrics["conversation_quality"] = "good"
        elif metrics["success_rate"] >= 70 and metrics["average_response_time"] < 8.0:
            metrics["conversation_quality"] = "fair"
        else:
            metrics["conversation_quality"] = "poor"
        
        # Determinar engajamento do usuário
        if metrics["total_interactions"] >= 5 and metrics["phases_covered"] >= 3:
            metrics["user_engagement"] = "high"
        elif metrics["total_interactions"] >= 3 and metrics["phases_covered"] >= 2:
            metrics["user_engagement"] = "medium"
        else:
            metrics["user_engagement"] = "low"
        
        return metrics
    
    def _calculate_system_performance(self, flow: RealConversationFlow) -> Dict[str, Any]:
        """Calcula métricas de performance do sistema"""
        if not flow.events:
            return {}
        
        response_times = [e.response_time for e in flow.events]
        errors = [e for e in flow.events if not e.success]
        
        return {
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": sorted(response_times)[len(response_times)//2],
            "error_count": len(errors),
            "error_rate": len(errors) / len(flow.events) * 100,
            "throughput": len(flow.events) / flow.total_duration if flow.total_duration > 0 else 0,
            "system_stability": "stable" if len(errors) == 0 else "unstable"
        }
    
    def analyze_real_patterns(self) -> Dict[str, Any]:
        """Analisa padrões nas conversas reais"""
        if not self.flows:
            return {"error": "No conversation flows to analyze"}
        
        analysis = {
            "total_conversations": len(self.flows),
            "total_events": sum(len(f.events) for f in self.flows),
            "average_duration": sum(f.total_duration for f in self.flows) / len(self.flows),
            "overall_success_rate": sum(f.success_metrics.get("success_rate", 0) for f in self.flows) / len(self.flows),
            "agent_transition_patterns": self._analyze_real_transitions(),
            "response_time_analysis": self._analyze_real_response_times(),
            "phase_patterns": self._analyze_real_phase_patterns(),
            "hook_summary": self._summarize_real_hooks(),
            "system_health": self._assess_real_system_health(),
            "business_insights": self._extract_business_insights()
        }
        
        return analysis
    
    def _analyze_real_transitions(self) -> Dict[str, Any]:
        """Analisa transições entre agentes no sistema real"""
        transitions = {}
        transition_times = []
        
        for flow in self.flows:
            for transition in flow.agent_transitions:
                key = f"{transition['from']} → {transition['to']}"
                transitions[key] = transitions.get(key, 0) + 1
                
                # Calcular tempo de transição se possível
                # (tempo entre última resposta do agente anterior e primeira do novo)
        
        return {
            "most_common": dict(sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5]),
            "total_transitions": sum(transitions.values()),
            "unique_patterns": len(transitions)
        }
    
    def _analyze_real_response_times(self) -> Dict[str, Any]:
        """Analisa tempos de resposta do sistema real"""
        all_times = []
        agent_times = {}
        
        for flow in self.flows:
            for event in flow.events:
                all_times.append(event.response_time)
                
                agent = event.agent_type.value
                if agent not in agent_times:
                    agent_times[agent] = []
                agent_times[agent].append(event.response_time)
        
        if not all_times:
            return {"error": "No response times to analyze"}
        
        all_times.sort()
        n = len(all_times)
        
        analysis = {
            "overall": {
                "min": min(all_times),
                "max": max(all_times),
                "average": sum(all_times) / n,
                "median": all_times[n//2],
                "p95": all_times[int(n * 0.95)] if n > 0 else 0,
                "p99": all_times[int(n * 0.99)] if n > 0 else 0
            },
            "by_agent": {}
        }
        
        # Análise por agente
        for agent, times in agent_times.items():
            if times:
                times.sort()
                n_agent = len(times)
                analysis["by_agent"][agent] = {
                    "average": sum(times) / n_agent,
                    "median": times[n_agent//2],
                    "min": min(times),
                    "max": max(times),
                    "count": n_agent
                }
        
        return analysis
    
    def _analyze_real_phase_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de fases no sistema real"""
        phase_sequences = []
        phase_durations = {}
        
        for flow in self.flows:
            sequence = [e.phase.value for e in flow.events]
            phase_sequences.append(sequence)
            
            # Calcular duração por fase
            for i, event in enumerate(flow.events):
                phase = event.phase.value
                if phase not in phase_durations:
                    phase_durations[phase] = []
                
                # Usar tempo de resposta como proxy para duração da fase
                phase_durations[phase].append(event.response_time)
        
        # Encontrar sequências mais comuns
        sequence_counts = {}
        for seq in phase_sequences:
            seq_str = " → ".join(seq)
            sequence_counts[seq_str] = sequence_counts.get(seq_str, 0) + 1
        
        return {
            "most_common_sequences": dict(sorted(sequence_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            "average_phases_per_conversation": sum(len(seq) for seq in phase_sequences) / len(phase_sequences) if phase_sequences else 0,
            "phase_durations": {phase: sum(times)/len(times) for phase, times in phase_durations.items() if times}
        }
    
    def _summarize_real_hooks(self) -> Dict[str, Any]:
        """Resumo dos hooks do sistema real"""
        summary = {}
        for hook in self.hooks:
            stats = hook.get_statistics()
            summary[hook.name] = {
                "events_captured": stats.get("total_events", 0),
                "priority": hook.priority,
                "success_rate": stats.get("success_rate", 0),
                "average_response_time": stats.get("average_response_time", 0)
            }
        return summary
    
    def _assess_real_system_health(self) -> Dict[str, Any]:
        """Avalia saúde do sistema real"""
        if not self.flows:
            return {"status": "unknown", "reason": "No data"}
        
        # Métricas agregadas
        total_events = sum(len(f.events) for f in self.flows)
        successful_events = sum(len([e for e in f.events if e.success]) for f in self.flows)
        success_rate = successful_events / total_events * 100 if total_events > 0 else 0
        
        avg_response_time = sum(
            sum(e.response_time for e in f.events) / len(f.events) 
            for f in self.flows if f.events
        ) / len(self.flows)
        
        # Determinar status
        issues = []
        if success_rate < 90:
            issues.append(f"Low success rate: {success_rate:.1f}%")
        if avg_response_time > 5.0:
            issues.append(f"High response time: {avg_response_time:.2f}s")
        
        if success_rate >= 95 and avg_response_time <= 3.0:
            status = "excellent"
        elif success_rate >= 85 and avg_response_time <= 5.0:
            status = "good"
        elif success_rate >= 70:
            status = "fair"
        else:
            status = "critical"
        
        return {
            "status": status,
            "success_rate": success_rate,
            "average_response_time": avg_response_time,
            "total_conversations": len(self.flows),
            "total_events": total_events,
            "issues": issues,
            "uptime": "100%"  # Placeholder - seria calculado com dados reais
        }
    
    def _extract_business_insights(self) -> Dict[str, Any]:
        """Extrai insights de negócio das conversas"""
        price_hook = next((h for h in self.hooks if h.name == "price_discussions"), None)
        scheduling_hook = next((h for h in self.hooks if h.name == "scheduling_requests"), None)
        property_hook = next((h for h in self.hooks if h.name == "property_inquiries"), None)
        
        insights = {
            "price_interest": len(price_hook.captured_events) if price_hook else 0,
            "scheduling_requests": len(scheduling_hook.captured_events) if scheduling_hook else 0,
            "property_inquiries": len(property_hook.captured_events) if property_hook else 0,
            "conversion_indicators": {
                "high_engagement": len([f for f in self.flows if f.success_metrics.get("user_engagement") == "high"]),
                "scheduling_rate": 0,  # Seria calculado baseado em dados reais
                "inquiry_to_schedule": 0  # Ratio de inquiries que levaram a agendamentos
            }
        }
        
        if property_hook and scheduling_hook:
            total_inquiries = len(property_hook.captured_events)
            total_scheduling = len(scheduling_hook.captured_events)
            if total_inquiries > 0:
                insights["conversion_indicators"]["inquiry_to_schedule"] = total_scheduling / total_inquiries * 100
        
        return insights
    
    def generate_real_monitoring_report(self) -> str:
        """Gera relatório de monitoramento do sistema real"""
        analysis = self.analyze_real_patterns()
        
        report = f"""
🔍 RELATÓRIO DE MONITORAMENTO - SISTEMA AGÊNTICO REAL
{'='*65}

📊 VISÃO GERAL:
• Total de Conversas: {analysis['total_conversations']}
• Total de Eventos: {analysis['total_events']}
• Duração Média: {analysis['average_duration']:.2f}s
• Taxa de Sucesso Geral: {analysis['overall_success_rate']:.1f}%

🏥 SAÚDE DO SISTEMA:
• Status: {analysis['system_health']['status'].upper()}
• Taxa de Sucesso: {analysis['system_health']['success_rate']:.1f}%
• Tempo Médio de Resposta: {analysis['system_health']['average_response_time']:.2f}s
• Uptime: {analysis['system_health']['uptime']}
"""
        
        if analysis['system_health']['issues']:
            report += "\n⚠️ PROBLEMAS IDENTIFICADOS:\n"
            for issue in analysis['system_health']['issues']:
                report += f"• {issue}\n"
        
        report += f"""
⏱️ ANÁLISE DE PERFORMANCE:
• Tempo Mínimo: {analysis['response_time_analysis']['overall']['min']:.2f}s
• Tempo Máximo: {analysis['response_time_analysis']['overall']['max']:.2f}s
• Tempo Médio: {analysis['response_time_analysis']['overall']['average']:.2f}s
• P95: {analysis['response_time_analysis']['overall']['p95']:.2f}s
• P99: {analysis['response_time_analysis']['overall']['p99']:.2f}s

🔄 TRANSIÇÕES MAIS COMUNS:
"""
        
        for transition, count in list(analysis['agent_transition_patterns']['most_common'].items())[:3]:
            report += f"• {transition}: {count} vezes\n"
        
        report += f"""
📈 INSIGHTS DE NEGÓCIO:
• Discussões sobre Preço: {analysis['business_insights']['price_interest']}
• Pedidos de Agendamento: {analysis['business_insights']['scheduling_requests']}
• Consultas sobre Propriedades: {analysis['business_insights']['property_inquiries']}
• Usuários Altamente Engajados: {analysis['business_insights']['conversion_indicators']['high_engagement']}
• Taxa Inquiry→Schedule: {analysis['business_insights']['conversion_indicators']['inquiry_to_schedule']:.1f}%

🎯 HOOKS ATIVOS:
"""
        
        for hook_name, stats in analysis['hook_summary'].items():
            report += f"• {hook_name}: {stats['events_captured']} eventos (P{stats['priority']})\n"
        
        return report

# Classe para integração com sistema de produção
class ProductionConversationMonitor:
    """Monitor de conversa para sistema de produção"""
    
    def __init__(self):
        self.analyzer = RealConversationAnalyzer()
        self.analyzer.create_production_hooks()
        self.logger = get_logger("production_monitor")
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        self.is_monitoring = True
        self.logger.info("🎬 Monitoramento de produção iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        self.logger.info("🛑 Monitoramento de produção parado")
    
    async def monitor_conversation(self, session_id: str, user_input: str, 
                                 agent_response: str, agent_type: str, 
                                 response_time: float, success: bool = True,
                                 context: Dict[str, Any] = None) -> None:
        """Monitora uma interação de conversa"""
        
        if not self.is_monitoring:
            return
        
        # Determinar fase da conversa baseada no conteúdo
        phase = self._determine_conversation_phase(user_input, agent_response)
        
        # Criar evento
        event = RealConversationEvent(
            timestamp=datetime.now(),
            agent_type=RealAgentType(agent_type),
            phase=phase,
            user_input=user_input,
            agent_response=agent_response,
            response_time=response_time,
            session_id=session_id,
            success=success,
            context=context or {},
            metadata={"monitored_at": datetime.now().isoformat()}
        )
        
        # Adicionar ao analisador
        self.analyzer.add_real_event(event)
    
    def _determine_conversation_phase(self, user_input: str, agent_response: str) -> RealConversationPhase:
        """Determina a fase da conversa baseada no conteúdo"""
        user_lower = user_input.lower()
        response_lower = agent_response.lower()
        
        if any(word in user_lower for word in ["hello", "hi", "start", "begin"]):
            return RealConversationPhase.GREETING
        elif any(word in user_lower for word in ["schedule", "appointment", "viewing", "visit"]):
            return RealConversationPhase.SCHEDULING
        elif any(word in user_lower for word in ["property", "apartment", "house", "details", "tell me"]):
            return RealConversationPhase.PROPERTY_DETAILS
        elif any(word in user_lower for word in ["search", "looking", "find", "need", "want"]):
            return RealConversationPhase.SEARCH_CRITERIA
        elif any(word in response_lower for word in ["error", "problem", "sorry", "failed"]):
            return RealConversationPhase.ERROR_HANDLING
        else:
            return RealConversationPhase.SEARCH_CRITERIA  # Default
    
    def get_live_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas em tempo real"""
        return self.analyzer.analyze_real_patterns()
    
    def generate_live_report(self) -> str:
        """Gera relatório em tempo real"""
        return self.analyzer.generate_real_monitoring_report()

async def main():
    """Demonstração do sistema de hooks real"""
    
    print("🔍 SISTEMA DE HOOKS DE CONVERSA REAL - DEMONSTRAÇÃO")
    print("="*60)
    
    # Criar monitor de produção
    monitor = ProductionConversationMonitor()
    monitor.start_monitoring()
    
    # Simular algumas conversas reais
    conversations = [
        {
            "session_id": "real_session_1",
            "interactions": [
                ("Hello, I'm looking for an apartment", "search_agent", "Hi! I'm here to help you find the perfect property. What are you looking for?"),
                ("I need 1 bedroom under $2000", "search_agent", "I found several properties that match your criteria. Let me show you the best options."),
                ("Tell me about the first property", "property_agent", "This property is excellent! It features 1 bedrooms and 1 bathrooms."),
                ("Can I schedule a viewing?", "scheduling_agent", "I'd be happy to schedule a viewing for you. What days work best?")
            ]
        },
        {
            "session_id": "real_session_2", 
            "interactions": [
                ("Hi, I need help finding a place", "search_agent", "Hello! I can help you find your perfect home. What's your budget?"),
                ("What's the price range for 2 bedrooms?", "search_agent", "2-bedroom apartments typically range from $2,500 to $4,000 per month."),
                ("Show me something in Miami", "property_agent", "Here's a great 2-bedroom in Miami with amazing amenities.")
            ]
        }
    ]
    
    print("💬 Simulando conversas reais...")
    
    for conv in conversations:
        session_id = conv["session_id"]
        print(f"\n🎭 Processando sessão: {session_id}")
        
        for i, (user_input, agent_type, agent_response) in enumerate(conv["interactions"]):
            # Simular tempo de resposta realista
            response_time = random.uniform(1.0, 4.0)
            
            print(f"   {i+1}. User: {user_input[:50]}...")
            print(f"      Agent ({agent_type}): {agent_response[:50]}... ({response_time:.2f}s)")
            
            # Monitorar interação
            await monitor.monitor_conversation(
                session_id=session_id,
                user_input=user_input,
                agent_response=agent_response,
                agent_type=agent_type,
                response_time=response_time,
                success=True,
                context={"mock_data": True}
            )
            
            # Simular delay entre interações
            await asyncio.sleep(0.5)
        
        # Finalizar sessão
        monitor.analyzer.end_conversation_monitoring(session_id)
    
    # Gerar relatório
    print("\n📊 RELATÓRIO DE MONITORAMENTO:")
    print(monitor.generate_live_report())
    
    print("\n✅ Demonstração de hooks reais concluída!")
    print("🔄 Sistema pronto para integração com produção")

if __name__ == "__main__":
    import random
    asyncio.run(main()) 