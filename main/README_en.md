# Technical Documentation: `xuanwu-device-server`

> Migration note (2026-03-28)
>
> This repository now includes the Python management host `xuanwu-management-server`, which is the default primary management host; legacy `manager-api` / `manager-web` are retained only for compatibility during migration.
>
> The current `XuanWu` AI endpoint is fixed to `http://xuanwu-ai:8000`, and management-domain requests are proxied through `xuanwu-management-server`.
>
> The local job stack is now `xuanwu-jobs + Redis`, and Docker deployments can scale worker replicas to support more platform jobs.

**Table of Contents:**

1.  [Introduction](#1-introduction)
2.  [Overall Architecture](#2-overall-architecture)
3.  [Component Deep Dive](#3-component-deep-dive)
    *   [3.1. `xuanwu-device-server` (Core AI Engine - Python Implementation)](#31-xuanwu-device-server-core-ai-engine---python-implementation)
    *   [3.2. `xuanwu-management-server` (Default Primary Management Host - Python Implementation)](#32-xuanwu-management-server-default-primary-management-host---python-implementation)
    *   [3.3. `manager-api` / `manager-web` (Java compatibility reference implementation)](#33-manager-api--manager-web-java-compatibility-reference-implementation)
4.  [Data Flow and Interaction Mechanisms](#4-data-flow-and-interaction-mechanisms)
5.  [Key Features Summary](#5-key-features-summary)
6.  [Deployment and Configuration Overview](#6-deployment-and-configuration-overview)

---

## 1. Introduction

The `xuanwu-device-server` project is a **comprehensive backend system** designed to support intelligent hardware based on ESP32. Its core goal is to enable developers to quickly build a robust server infrastructure that can understand natural language commands, interact efficiently with various AI services (for speech recognition, natural language understanding, and speech synthesis), manage IoT devices, and provide a web-based user interface for system configuration and management. By integrating multiple cutting-edge technologies into a cohesive and extensible platform, this project aims to simplify and accelerate the development process of customizable voice assistants and intelligent control systems. It is not just a simple server, but a bridge connecting hardware, AI capabilities, and user management.

---

## 2. Overall Architecture

The `xuanwu-device-server` system adopts a **distributed, multi-component collaborative** architectural design, ensuring modularity, maintainability, and scalability. Each core component has its specific role and works in coordination. The main components include:

1.  **ESP32 Hardware (Client Device):**
    This is the physical smart hardware device that end-users directly interact with. Its main responsibilities include:
    *   Capturing user voice commands.
    *   Securely sending captured raw audio data to `xuanwu-device-server` for processing.
    *   Receiving synthesized voice responses from `xuanwu-device-server` and playing them through speakers.
    *   Controlling other connected peripherals or IoT devices (such as smart bulbs, sensors, etc.) based on instructions received from `xuanwu-device-server`.

2.  **`xuanwu-device-server` (Core AI Engine - Python Implementation):**
    This Python-based server is the "brain" of the entire system, responsible for handling all voice-related logic and AI interactions. Its key responsibilities are detailed as follows:
    *   Establishing **stable, low-latency real-time bidirectional communication links** with ESP32 devices through the WebSocket protocol.
    *   Receiving audio streams from ESP32 and using Voice Activity Detection (VAD) technology to precisely segment valid speech segments.
    *   Integrating and calling Automatic Speech Recognition (ASR) services (configurable for local or cloud), converting speech segments to text.
    *   Interacting with Large Language Models (LLMs) to parse user intent, generate intelligent responses, and support complex natural language understanding tasks.
    *   Managing context information and user memory in multi-turn dialogues to provide coherent interaction experiences.
    *   Calling Text-to-Speech (TTS) services to synthesize natural and fluent speech from LLM-generated text responses.
    *   Executing custom commands through a flexible **plugin system**, including IoT device control logic.
    *   Obtaining its detailed runtime operation configuration from the `manager-api` service.

3.  **`xuanwu-management-server` (Default Primary Management Host - Python Implementation):**
    This is the recommended Python management host for the current architecture. It owns the control-plane and management-domain entrypoints and serves as the preferred runtime configuration source for `xuanwu-device-server`. Its core responsibilities include:
    *   Exposing the new `/control-plane/v1/*` management and control-plane APIs.
    *   Acting as the default runtime configuration source for `xuanwu-device-server`.
    *   Proxying agent-configuration requests to `XuanWu` through `/control-plane/v1/xuanwu/*`.
    *   Gradually absorbing the management responsibilities previously held by `manager-api` / `manager-web`.

4.  **`manager-api` / `manager-web` (Java compatibility reference implementation):**
    These modules remain in the repository for migration compatibility, deployment reference, and feature inventory only. They are no longer the recommended default path. `xuanwu-device-server` falls back to this Java management chain only when legacy compatibility mode is explicitly enabled.

**High-Level Interaction Flow Overview:**

*   **Voice Interaction Main Line:** After the **ESP32 device** captures user voice, it transmits audio data in real-time to **`xuanwu-device-server`** through **WebSocket**. After `xuanwu-device-server` completes a series of AI processing (VAD, ASR, LLM interaction, TTS), it sends the synthesized voice response back to the ESP32 device for playback through WebSocket. All real-time interactions directly related to voice are completed in this link.
*   **Management Configuration Main Line:** Administrators enter the new Python management path through **`xuanwu-management-server`**; agent-configuration requests then continue through `xuanwu-management-server -> XuanWu` for proxying and persistence.
*   **Configuration Synchronization:** **`xuanwu-device-server`** actively pulls its preferred runtime configuration from **`xuanwu-management-server`**. It only falls back to `manager-api` when legacy compatibility mode is explicitly enabled.

This layered architecture lets `xuanwu-device-server` focus on real-time runtime processing, `xuanwu-management-server` focus on management and control-plane responsibilities, and `XuanWu` own the agent/configuration domain. The legacy Java management modules are retained only as compatibility references.

```
xuanwu-device-server
  ├─ xuanwu-device-server Port 8000 Python development Responsible for ESP32 communication
  ├─ xuanwu-management-server Port 18082 Python development Responsible for the default primary management host
  ├─ manager-web Port 8001 Node.js+Vue development Java compatibility reference implementation
  ├─ manager-api Port 8002 Java development Java compatibility reference implementation
  └─ Mobile management has been retired and will be absorbed by the Python control plane
```

---

## 3. Component Deep Dive

### 3.1. `xuanwu-device-server` (Core AI Engine - Python Implementation)

The `xuanwu-device-server` is the intelligent core of the system, responsible for processing voice interactions, interfacing with AI services, and managing communication with ESP32 devices.

*   **Purpose:**
    *   To provide real-time processing of voice commands from ESP32 devices.
    *   To integrate with various AI services for Speech-to-Text (ASR), Natural Language Understanding (via Large Language Models - LLMs), Text-to-Speech (TTS), Voice Activity Detection (VAD), Intent Recognition, and Memory.
    *   To manage dialogue flow and context with users.
    *   To execute custom functions and control IoT devices based on user commands.
    *   To be dynamically configurable through `xuanwu-management-server`, with `manager-api` retained only as an explicit compatibility fallback.

*   **Core Technologies:**
    *   **Python 3:** The primary programming language.
    *   **Asyncio:** Python's asynchronous programming framework, crucial for handling concurrent WebSocket connections and non-blocking I/O for AI service API calls.
    *   **`websockets` Library:** For WebSocket server implementation.
    *   **HTTP Client (e.g., `aiohttp`, `httpx`):** For asynchronous HTTP requests to `manager-api` and external AI services.
    *   **YAML (PyYAML):** For local configuration file parsing.

*   **Key Implementation Aspects:**

    1.  **AI Service Provider Pattern (`core/providers/`):**
        *   **Concept:** A flexible design for integrating AI services. Each service type (ASR, TTS, LLM, etc.) has an abstract base class defining a common interface. Concrete classes implement this interface for specific vendors or local models.
        *   **Benefit:** Allows easy switching of AI service backends via configuration and simplifies adding new service integrations.
        *   **Initialization:** `core/utils/modules_initialize.py` acts as a factory to load and instantiate configured providers.

    2.  **WebSocket Communication & Connection Handling (`core/websocket_server.py`, `core/connection.py`):**
        *   **Server Setup:** Manages WebSocket connections from ESP32 devices.
        *   **Connection Isolation:** Each ESP32 client gets a dedicated `ConnectionHandler` instance, isolating its session state and dialogue.
        *   **Dynamic Configuration Updates:** Can fetch updated configurations from `manager-api` and re-initialize AI service modules live, without a full server restart.

    3.  **Message Handling & Dialogue Flow (`core/handle/`):**
        *   Employs a modular handler pattern. The `ConnectionHandler` dispatches message processing to specialized modules based on message type or dialogue phase (e.g., `receiveAudioHandle.py` for audio input, `intentHandler.py` for NLU, `functionHandler.py` for plugin execution, `sendAudioHandle.py` for TTS output).

    4.  **Plugin System for Extensible Functions (`plugins_func/`):**
        *   **Purpose:** Allows adding custom "skills" (e.g., weather, news, Home Assistant control).
        *   **Mechanism:** Plugins define functions and schemas. The LLM can request execution of these functions (function calling). `loadplugins.py` and `register.py` manage plugin discovery and registration.

    5.  **Configuration Management (`config/`):**
        *   Loads settings from a local `config.yaml` and merges them with configurations fetched from `manager-api` (via `manage_api_client.py`), enabling remote dynamic configuration.
        *   `logger.py` sets up structured application logging.
        *   `config/assets/` stores predefined audio files for system notifications.

    6.  **Auxiliary HTTP Server (`core/http_server.py`):**
        *   Handles specific HTTP requests, notably for OTA firmware updates (`/xuanwu/ota/`) and other utility endpoints.

### 3.2. `manager-api` (Management Backend - Java Spring Boot Implementation)

The `manager-api` component is a backend server built using Java and the Spring Boot framework, serving as the administrative hub.

*   **Purpose:**
    *   Provide a secure RESTful API for the `manager-web` frontend.
    *   Act as a centralized configuration provider for `xuanwu-device-server`.
    *   Manage persistent data (users, devices, AI configurations, voice timbres, OTA firmware).

*   **Core Technologies:**
    *   **Java 21 & Spring Boot 3:** Core language and framework.
    *   **Spring MVC:** For building REST controllers.
    *   **MyBatis-Plus:** ORM for database interaction with MySQL.
    *   **MySQL:** Relational database.
    *   **Druid:** JDBC connection pool.
    *   **Redis (Spring Data Redis):** For caching.
    *   **Apache Shiro:** Security framework for authentication and authorization.
    *   **Liquibase:** Database schema migration.
    *   **Knife4j:** OpenAPI (Swagger) API documentation.
    *   **Maven:** Build and dependency management.

*   **Key Implementation Aspects:**

    1.  **Modular Architecture (`modules/` package):**
        *   Business logic is organized into distinct modules (e.g., `sys` for users/roles, `agent` for assistant configs, `device` for ESP32s, `config` for `xuanwu-device-server` settings, `security`, `timbre`, `ota`).
        *   Each module typically follows a layered pattern: Controller, Service, DAO (Mapper), Entity, DTO.

    2.  **Layered Architecture:**
        *   **Controller Layer (`@RestController`):** Defines API endpoints, handles HTTP request/response.
        *   **Service Layer (`@Service`):** Contains business logic, transaction management.
        *   **Data Access Layer (MyBatis-Plus Mappers):** Interacts with the MySQL database.

    3.  **Common Functionalities (`common/` package):**
        *   Provides shared code: base classes, global configurations (Spring, MyBatis, Redis, Knife4j), custom annotations (e.g., `@LogOperation`), AOP aspects, global exception handling, utility classes, and XSS protection.

    4.  **Security (Apache Shiro):**
        *   Manages user authentication and permissions for accessing API endpoints. Configured with Shiro Realms and security filters.

    5.  **Database Schema Management (Liquibase):**
        *   Ensures consistent database structure across environments through versioned schema changes.

### 3.3. `manager-web` (Web Control Panel - Vue.js Implementation)

The `manager-web` is a Single Page Application (SPA) providing the administrative user interface.

*   **Purpose:**
    *   Offer a web-based control panel for system configuration and management.
    *   Enable administrators to configure `xuanwu-device-server`'s AI services, manage users and devices, customize voice timbres, and handle OTA updates.

*   **Core Technologies:**
    *   **Vue.js 2 & Vue CLI:** Core JavaScript framework and build tools.
    *   **Vue Router:** For client-side routing within the SPA.
    *   **Vuex:** For centralized state management.
    *   **Element UI:** UI component library for a consistent look and feel.
    *   **SCSS:** CSS preprocessor.
    *   **HTTP Client (Flyio or Axios):** For API calls to `manager-api`.
    *   **Workbox:** For PWA features (caching, service worker).
    *   **Opus Libraries:** For potential in-browser audio recording/playback.

*   **Key Implementation Aspects:**

    1.  **SPA Structure:** Single HTML page with dynamic view updates.
    2.  **Component-Based Architecture:** UI built from reusable Vue components (`.vue` files in `src/views/` for pages and `src/components/` for smaller elements).
    3.  **Client-Side Routing (`src/router/index.js`):** Maps browser URLs to view components, with route guards for authentication.
    4.  **State Management (`src/store/index.js`):** Vuex manages global state (user info, device lists, etc.) via state, getters, mutations, and actions (often involving API calls).
    5.  **API Communication (`src/apis/`):** Modularized API service files make asynchronous calls to `manager-api`.
    6.  **Build Process & PWA Features:** Vue CLI (Webpack) bundles assets. Workbox enables PWA features like caching.
    7.  **Environment Configuration (`.env` files):**
        *   The `.env` (and `.env.development`, `.env.production`, etc.) files in the project root directory are used to define environment variables. These variables (such as `VUE_APP_API_BASE_URL` to specify the base URL of `manager-api`) can be accessed in the application code through `process.env.VUE_APP_XXX`, allowing configuration of different parameters for different build environments (development, testing, production).

`manager-web` constructs a powerful, maintainable, and user-friendly management interface through the comprehensive application of these technologies, providing solid frontend support for the configuration and monitoring of the `xuanwu-device-server` system.

## 4. Data Flow and Interaction Mechanisms

The `xuanwu-device-server` system coordinates work through well-defined data flows and interaction protocols between components. The main communication methods rely on WebSocket protocol optimized for real-time interaction and RESTful API suitable for client-server requests.

**4.1. Core Voice Interaction Flow (ESP32 Device <-> `xuanwu-device-server`)**

This flow is real-time, primarily using WebSocket for low-latency, bidirectional data exchange.

*   **Communication Protocol Documentation:**
    *   Detailed communication protocol documentation can be accessed at: https://ccnphfhqs21z.feishu.cn/wiki/M0XiwldO9iJwHikpXD5cEx71nKh
    *   This document details the WebSocket communication protocol between ESP32 devices and `xuanwu-device-server`, including:
        *   Connection establishment and handshake process
        *   Audio data transmission format
        *   Control command format
        *   Status report format
        *   Error handling mechanism

*   **Connection Establishment and Handshake:**
    *   The ESP32 device, as a client, actively initiates a WebSocket connection request to the specified endpoint of `xuanwu-device-server` (e.g., `ws://<server-IP>:<WebSocket-port>/xuanwu/v1/`).
    *   `xuanwu-device-server` (`core/websocket_server.py`) receives the connection and instantiates an independent `ConnectionHandler` object for each successfully connected ESP32 device to manage the entire lifecycle of that session.
    *   After the connection is established, an initial handshake process may be executed (handled by `core/handle/helloHandle.py`) to exchange device identification, authentication information, protocol version, or basic status.

*   **Audio Uplink Transmission (ESP32 -> `xuanwu-device-server`):**
    *   After a user speaks to the ESP32 device, the device's microphone captures raw audio data (usually in PCM or compressed formats like Opus).
    *   The ESP32 pushes these audio data chunks as WebSocket **binary messages** in real-time to the corresponding `ConnectionHandler` in `xuanwu-device-server`.
    *   The server-side `core/handle/receiveAudioHandle.py` module is responsible for receiving, buffering, and processing these audio data.

*   **AI Core Processing (within `xuanwu-device-server`):**
    *   **VAD (Voice Activity Detection):** `receiveAudioHandle.py` uses the configured VAD provider (such as SileroVAD) to analyze the audio stream, accurately identifying the start and end points of speech, filtering out silent or noise segments.
    *   **ASR (Automatic Speech Recognition):** Detected valid speech segments are sent to the configured ASR provider (local such as FunASR, or cloud services). The ASR engine converts audio signals into text strings.
    *   **NLU/LLM (Natural Language Understanding/Large Language Model):** The ASR output text, along with the current dialogue context history obtained from the Memory provider, and the description schemas of available functions (tools) loaded from `plugins_func/`, are passed to the configured LLM provider.
    *   **Function Call Execution (if LLM decides needed):** If the LLM analysis determines that an external function needs to be called (e.g., querying weather, controlling home appliances), it generates a structured function call request. `core/handle/functionHandler.py` receives this request, finds and executes the corresponding Python function defined in `plugins_func/`, and returns the function's execution result to the LLM. The LLM then generates the final natural language response based on this result.
    *   **Response Generation:** The LLM synthesizes all information (user input, context, function call results, etc.) to generate the final text response.
    *   **Memory Update:** The current round of interaction (user question, LLM response, possible function calls) is processed by the Memory provider to update the dialogue history for subsequent interactions.
    *   **TTS (Text-to-Speech):** The final text response generated by the LLM is sent to the configured TTS provider, which synthesizes the text into a speech data stream (e.g., MP3 or WAV format).

*   **Audio Downlink Response (`xuanwu-device-server` -> ESP32):**
    *   The speech data stream synthesized by the TTS provider is sent in real-time as WebSocket **binary messages** back to the ESP32 device through the `core/handle/sendAudioHandle.py` module.
    *   The ESP32 device receives these audio data chunks and immediately plays them to the user through the speaker.

*   **Control and Status Messages (Bidirectional):**
    *   In addition to audio streams, ESP32 and `xuanwu-device-server` also exchange **text messages** through WebSocket, these messages are usually encapsulated in JSON format.
    *   **ESP32 -> Server:** The device may send status reports (such as network conditions, microphone status), error codes, or specific control commands (e.g., "stop TTS playback" triggered by user button press).
    *   **Server -> ESP32:** The server may send control instructions to the device (such as "start listening", "stop listening", adjust sensitivity, send specific configuration parameters).
    *   Modules like `core/handle/abortHandle.py` (handling interrupt requests), `core/handle/reportHandle.py` (handling device reports) are responsible for parsing and responding to these control/status messages.

**4.2. Management and Configuration Flow (`xuanwu-management-server` <-> `XuanWu` <-> `xuanwu-device-server`)**

This flow primarily relies on HTTP/HTTPS-based RESTful API for request-response interactions.

*   **Administrator Management Main Line (`management frontend` -> `xuanwu-management-server`):**
    *   The recommended management entrypoint is now `xuanwu-management-server`. Requests first enter the Python management host, which owns control-plane responsibilities, management-domain logic, and upstream proxying.
    *   Requests related to agent configuration continue through `xuanwu-management-server -> XuanWu` for proxying, validation, and persistence.

*   **Runtime Configuration Synchronization (`xuanwu-management-server` -> `xuanwu-device-server`):**
    *   `xuanwu-device-server` now prefers dynamic runtime configuration from `xuanwu-management-server`.
    *   This path is implemented by modules such as `config/config_loader.py` and `config/xuanwu_management_client.py`.
    *   `manager-api` is used only when legacy compatibility mode is explicitly enabled.

*   **OTA and control-plane data:**
    *   In the default primary path, OTA metadata and control-plane configuration should be owned by the Python management host.
    *   Devices still receive OTA download URLs or control instructions through the runtime path of `xuanwu-device-server`.
    *   If the old Java management chain is still used, it is now documented as compatibility behavior rather than the default path.

**4.3. Main Protocol Summary:**

*   **WebSocket:** Selected for the communication link between ESP32 and `xuanwu-device-server` because it is very suitable for real-time, low-latency, bidirectional data stream transmission (especially audio), as well as asynchronous control message delivery.
*   **RESTful APIs (based on HTTP/HTTPS, usually using JSON as the data exchange format):** This is the standard service-to-service communication model. It is now used primarily between `xuanwu-management-server` and `XuanWu`, and between `xuanwu-device-server` and `xuanwu-management-server`. `manager-api` remains only as a compatibility-path dependency.

This multi-protocol communication strategy ensures that different types of interaction requirements within the system can be handled efficiently and appropriately, balancing real-time performance and standardized request-response patterns.

---

## 5. Key Features Summary

The `xuanwu-device-server` system provides a series of rich features aimed at supporting developers in building advanced voice control applications:

1.  **Comprehensive Voice Interaction Backend:** Provides an end-to-end solution from voice capture guidance to response generation and action execution.
2.  **Modular and Pluggable AI Services:**
    *   Supports a wide range of ASR (Automatic Speech Recognition), LLM (Large Language Model), TTS (Text-to-Speech), VAD (Voice Activity Detection), Intent Recognition, and Memory providers.
    *   Allows dynamic selection and configuration of these services (including cloud-based APIs and local models) to balance cost, performance, privacy, and language requirements.
3.  **Advanced Dialogue Management:**
    *   Supports natural interaction, with wake word to start dialogue, manual (push-to-talk) dialogue, and real-time interruption of system responses.
    *   Includes contextual memory to maintain coherence in multi-turn dialogues.
    *   Has automatic sleep mode after a period of inactivity.
4.  **Multi-language Capabilities:**
    *   Supports recognition and synthesis in multiple languages, including Mandarin, Cantonese, English, Japanese, and Korean (specific capabilities depend on the selected ASR/LLM/TTS providers).
5.  **Extensible Functions through Plugins:**
    *   Powerful plugin system allows developers to add custom "skills" or functions (e.g., getting weather, controlling smart home devices, accessing news).
    *   These functions can be triggered by the LLM using its function calling capability, based on provided schemas.
    *   Built-in support for Home Assistant integration.
6.  **IoT Device Control:**
    *   Designed to manage and control smart home devices and other IoT hardware through voice commands, utilizing the plugin system.
7.  **Web-based Management Console (`manager-web` & `manager-api`):**
    *   Provides a comprehensive graphical interface for:
        *   System configuration (AI service selection, API keys, operation parameters).
        *   Role-based access control user management.
        *   ESP32 device registration and management.
        *   Voice timbre/TTS voice customization.
        *   OTA (Over-The-Air) firmware update management for ESP32 devices.
        *   System parameter and dictionary management.
8.  **Flexible Deployment Options:**
    *   Supports deployment through Docker containers (for simplified server-only or full-stack setup) and directly from source code, adapting to various environments and user expertise.
9.  **Dynamic Remote Configuration:**
    *   `xuanwu-device-server` can obtain its configuration from `manager-api`, allowing real-time updates of AI providers and settings without restarting the server.
10. **Open Source and Community-Driven:**
    *   Licensed under MIT License, encouraging transparency, collaboration, and community contribution.
11. **Cost-Effective Solution:**
    *   Provides an "Entry Level Free Settings" path, utilizing free tiers of AI services or local models, making it easy to experiment and for personal projects.
12. **Progressive Web Application (PWA) Features:**
    *   The `manager-web` control panel includes Service Worker integration to enhance caching and potential offline access capabilities.
13. **Detailed API Documentation:**
    *   `manager-api` provides OpenAPI (Swagger) documentation through Knife4j for clear understanding and testing of its RESTful endpoints.

These features together make `xuanwu-device-server` a powerful, adaptable, and user-friendly platform for building complex voice interaction applications.

---

## 6. Deployment and Configuration Overview

The `xuanwu-device-server` system is designed with flexibility in mind, providing multiple deployment methods and comprehensive configuration options to adapt to different usage scenarios and requirements.

**Deployment Options:**

The project can be deployed in multiple ways, mainly including using Docker to simplify the installation process, or deploying directly from source code for greater control and development.

1.  **Docker-based Deployment:**
    *   **Simplified Installation (Only `xuanwu-device-server`):** This option deploys only the runtime service and is suitable when voice AI processing and device runtime flow are the primary goals.
    *   **Full Module Installation (Default Primary Path):** The recommended current path deploys `xuanwu-device-server + xuanwu-management-server`, with `XuanWu` connected as the external agent service.
    *   **Legacy Java compatibility mode:** If the old management chain is still required, `manager-api` / `manager-web` / MySQL / Redis are brought up explicitly through the `legacy-java profile`.
    *   The project uses `docker-compose_all.yml` to orchestrate these services. The default `docker compose -f docker-compose_all.yml up -d` follows the Python-primary path, while `docker compose --profile legacy-java -f docker-compose_all.yml up -d` enables the legacy Java management stack.

2.  **Source Code Deployment:**
    *   The current default primary path is `xuanwu-device-server + xuanwu-management-server + XuanWu`.
    *   `manager-api` / `manager-web` and their database dependencies are only required when maintaining the legacy compatibility path.
    *   This approach is typically used for project development, deep customization, debugging, or in production scenarios with special environmental requirements.

**Configuration Management:**

Configuration is key to customizing system behavior, especially in selecting AI service providers and managing API keys.

1.  **`xuanwu-device-server` Configuration:**
    *   **Local `config.yaml`:** A main YAML format configuration file located in the `xuanwu-device-server` root directory. It defines server ports, selected AI service providers (ASR, LLM, TTS, VAD, Intent Recognition, Memory modules, etc.), their respective API keys or model paths, plugin configurations, and log levels.
    *   **Dynamic Remote Configuration:** `xuanwu-device-server` now prefers runtime configuration from `xuanwu-management-server`, while agent-domain requests are proxied onward to `XuanWu`. This provides:
        *   **Centralized Management:** Configuration can be centralized in the Python management host before being distributed to runtime and agent domains.
        *   **Dynamic Updates:** `xuanwu-device-server` can refresh configuration and reinitialize AI modules without a full restart.
    *   `config/config_loader.py`, `config/xuanwu_management_client.py`, and legacy `config/manage_api_client.py` handle configuration loading together, with `manager-api` active only in explicit compatibility mode.

2.  **`xuanwu-management-server` Configuration:**
    *   Key configuration includes the management-host listen address, control-plane auth secret, and the upstream `XuanWu` endpoint (currently fixed to `http://xuanwu-ai:8000`).

3.  **Legacy Java Configuration:**
    *   `manager-api` / `manager-web` settings remain in the repository as compatibility references.
    *   They matter only when `legacy-java profile` or `manager-api.enabled=true` is intentionally used.

4.  **Predefined Configuration Schemes:**
    *   The project documentation (usually README) will recommend some common configuration combinations, for example:
        *   **"Entry Level Free Settings":** This scheme aims to utilize free tier quotas of cloud AI services or completely free local models to minimize users' initial usage costs and operating expenses.
        *   **"Full Streaming Configuration":** This scheme prioritizes system response speed and interaction fluency, typically choosing AI services that support streaming processing (possibly paid).
    *   These predefined schemes provide guidance for configuring upstream capabilities for `xuanwu-device-server` and `XuanWu`.

In the current full deployment model, `xuanwu-management-server` is the recommended primary operations entrypoint. `manager-web` remains only as a legacy compatibility reference interface.

---


