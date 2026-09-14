FROM node:22-alpine AS base

WORKDIR /app

# Habilita pnpm via corepack — mais estável que instalar globalmente
RUN corepack enable && corepack prepare pnpm@latest --activate

# ─── Dev ────────────────────────────────────────────────────────────────────
FROM base AS dev

# Não instala nada aqui — o volume monta ./apps/web em /app
# e o CMD instala as deps na primeira execução.
# O node_modules fica num volume separado (web_node_modules) para não
# ser sobrescrito pelo bind mount do código fonte.

EXPOSE 5173

CMD ["sh", "-c", "pnpm install --frozen-lockfile && pnpm dev --host 0.0.0.0 --port 5173"]


# ─── Deps (cache layer) ──────────────────────────────────────────────────────
FROM base AS deps

# Copia só os arquivos de manifesto primeiro para maximizar cache
# Se apenas o código mudar (mas não package.json/lock), esse layer é reusado
COPY package.json pnpm-lock.yaml ./

# pnpm-workspace.yaml só é necessário em monorepos onde este package
# faz parte de um workspace maior. Se apps/web é standalone, remova.
# COPY pnpm-workspace.yaml ./

RUN pnpm install --frozen-lockfile --prod=false


# ─── Build ──────────────────────────────────────────────────────────────────
FROM deps AS build

# Copia o restante do código (node_modules já existem do stage deps)
COPY . .

# Garante que variáveis de build estejam disponíveis se necessário
# ARG VITE_API_URL
# ENV VITE_API_URL=$VITE_API_URL

RUN pnpm build-only


# ─── Prod ───────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS prod

# Remove a config default do nginx que não serve para SPAs
RUN rm /etc/nginx/conf.d/default.conf

# Config específica para SPA — fallback para index.html em qualquer rota
COPY infra/nginx/conf.d/spa.conf /etc/nginx/conf.d/default.conf

# Copia o build do Vite
COPY --from=build /app/dist/ /usr/share/nginx/html/

# Usuário não-root por segurança
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 80