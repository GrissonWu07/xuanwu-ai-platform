# Docker Hub Release Automation Design

## Goal

Build and publish the active platform service images from GitHub Actions to Docker Hub, with the first public release tagged as `v0.7.1`.

## Scope

This design covers the release automation for these active services:

- `xuanwu-portal`
- `xuanwu-device-gateway`
- `xuanwu-management-server`
- `xuanwu-iot-gateway`
- `xuanwu-jobs`

It does not attempt to publish infrastructure images such as PostgreSQL or Mosquitto.

## Release Registry

The target registry is Docker Hub.

Each service is published as an independent repository under the fixed Docker Hub namespace `xuanwu`:

- `xuanwu/xuanwu-portal`
- `xuanwu/xuanwu-device-gateway`
- `xuanwu/xuanwu-management-server`
- `xuanwu/xuanwu-iot-gateway`
- `xuanwu/xuanwu-jobs`

Authentication uses:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

`DOCKERHUB_USERNAME` is used only for authentication. It must have permission to push into the `xuanwu` namespace, but it does not control the published image path.

## Tag Strategy

The first release version is `v0.7.1`.

Tag behavior:

- push to `main`
  - publishes `latest`
  - publishes `sha-<shortsha>`
- git tag `v0.7.1`
  - publishes `v0.7.1`
  - publishes `0.7.1`
  - publishes `latest`
- manual `workflow_dispatch`
  - publishes the same tag set as `main` unless run against a version tag ref

This keeps the first version easy to pull while still supporting immutable image references.

## Build Strategy

### Unified workflow

Use one workflow:

- `.github/workflows/dockerhub-release.yml`

The workflow uses a build matrix for the five active services.

Each matrix entry defines:

- image name
- build context
- Dockerfile path

### Multi-platform output

Images publish for:

- `linux/amd64`
- `linux/arm64`

## Dockerfile Strategy

The current repository already has service Dockerfiles for:

- `main/xuanwu-portal/Dockerfile`
- `main/xuanwu-iot-gateway/Dockerfile`

This release automation adds missing service Dockerfiles for:

- `main/xuanwu-device-gateway/Dockerfile`
- `main/xuanwu-management-server/Dockerfile`
- `main/xuanwu-jobs/Dockerfile`

These Dockerfiles become the canonical release build inputs for Docker Hub.

Legacy root-level image build files remain only if they are still needed for local compatibility. The GitHub workflow should stop publishing the old GHCR image names.

## Workflow Behavior

The workflow must:

1. Check out the repository
2. Set up QEMU
3. Set up Buildx
4. Log in to Docker Hub
5. Generate tags and labels with `docker/metadata-action`
6. Build and push the five images

## Replacement of Legacy Workflows

Current GHCR-oriented workflows are legacy and should no longer be the active publish path:

- `.github/workflows/docker-image.yml`
- `.github/workflows/build-base-image.yml`

The new Docker Hub workflow becomes the single active image release path.

Preferred cleanup:

- remove the old GHCR workflows
- publish only through Docker Hub

## Documentation Requirements

Update repository documentation to describe:

- required GitHub secrets
- image names
- tag behavior
- release trigger behavior

At minimum, update:

- `README.md`
- `README_zh.md`
- `docs/Deployment.md`

## Validation

Add repository tests that verify:

- the Docker Hub workflow exists
- the workflow references the five active images
- the workflow uses Docker Hub credentials
- the three newly required service Dockerfiles exist
- the workflow listens to `main`, version tags, and `workflow_dispatch`

## Non-Goals

This design does not include:

- signing images
- SBOM generation
- provenance attestation
- automatic deployment after publish

Those can be added later after `v0.7.1` release automation is stable.
