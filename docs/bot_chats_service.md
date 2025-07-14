# BotChatsService 메모리 관리 구조 및 사용법

## 개요
- BotChatsService는 소셜봇과 유자 간 1:1 채팅 기능을 지원하기 위해 stream_id별로 독립적인 대화 기록(메모리)을 관리합니다.
- Langchain의 ConversationBufferMemory를 활용하여, 각 stream_id별로 최근 5개의 대화만 저장합니다.

## 주요 메서드 및 역할

### get_memory(stream_id: str)
- 해당 stream_id의 ConversationBufferMemory 인스턴스를 반환하거나, 없으면 새로 생성합니다.
- 내부적으로 self.memory_dict[stream_id]에 저장/관리됩니다.

### add_message_to_memory(stream_id: str, role: str, content: str)
- stream_id별 메모리에 새로운 메시지를 추가합니다.
- role은 'user', 'ai' 등 역할 구분, content는 메시지 본문입니다.

### get_recent_messages(stream_id: str)
- stream_id별 최근 대화 기록(최대 5개)을 리스트로 반환합니다.
- 각 메시지는 {"role": ..., "content": ...} 형태입니다.

### delete_memory(stream_id: str)
- 해당 stream_id의 메모리(ConversationBufferMemory)를 메모리에서 삭제(파기)합니다.
- 스트리밍 중단, 에러, 타임아웃 등 상황에서 호출됩니다.

### generate_bot_chat(request: BotChatsRequest)
- stream_id별로 대화 기록을 불러오고, 유저 메시지를 추가한 뒤, 최근 대화 맥락을 LLM 프롬프트로 활용하여 AI 응답을 생성합니다.
- 생성된 AI 응답도 메모리에 추가합니다.
- 예외 발생 시 해당 stream_id의 메모리를 삭제합니다.

## 서비스 흐름 예시
1. 사용자가 채팅을 입력하면, 해당 stream_id의 메모리에 메시지가 추가됩니다.
2. 최근 5개 대화 맥락을 기반으로 LLM이 응답을 생성합니다.
3. 생성된 AI 응답도 메모리에 추가되어, 다음 대화 시 맥락이 자연스럽게 이어집니다.
4. 스트리밍 중단/에러/타임아웃 등 상황에서는 delete_memory로 해당 대화 기록을 즉시 파기합니다.

## 활용 시나리오
- 1:1 채팅, 스트리밍 챗봇, 대화 맥락 유지가 필요한 다양한 서비스에 적용 가능
- 메모리 사용량을 효율적으로 관리하며, 유저별/스트림별로 독립적인 대화 흐름을 보장 