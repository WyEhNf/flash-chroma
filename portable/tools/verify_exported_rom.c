/* Host-side verifier for generated const ROM arrays. Not firmware I/O code. */
#include "flash_chroma.h"
#include <stdio.h>
#include <string.h>

static jshc_p_model models[JSHC_P_STAGES];
static jshc_p_chain chain;
static uint8_t pixels[65536u * 3u];

int main(int argc, char **argv) {
    FILE *stream;
    unsigned stage;
    size_t payload = 0;
    jshc_p_status status;
    if (argc != 3 || (strcmp(argv[1], "blobs") && strcmp(argv[1], "cube"))) return 2;
    stream = fopen(argv[2], "wb");
    if (stream == NULL) return 3;
    for (stage = 0; stage < JSHC_P_STAGES; ++stage) payload += flash_chroma_blob_bytes[stage];
    if (!strcmp(argv[1], "blobs")) {
        for (stage = 0; stage < JSHC_P_STAGES; ++stage) {
            size_t bytes = flash_chroma_blob_bytes[stage];
            if (fwrite(flash_chroma_blobs[stage], 1u, bytes, stream) != bytes) return 4;
        }
    } else {
        uint32_t base;
        status = flash_chroma_prepare(models, &chain, 0u);
        if (status != JSHC_P_OK) return 5;
        for (base = 0; base < 16777216u; base += 65536u) {
            uint32_t index;
            for (index = 0; index < 65536u; ++index) {
                uint32_t value = base + index;
                pixels[3u * index] = (uint8_t)(value >> 16u);
                pixels[3u * index + 1u] = (uint8_t)(value >> 8u);
                pixels[3u * index + 2u] = (uint8_t)value;
            }
            status = jshc_p_apply_rgb8(&chain, pixels, sizeof pixels, sizeof pixels,
                    pixels, sizeof pixels, sizeof pixels, 65536u, 1u);
            if (status != JSHC_P_OK) return 6;
            if (fwrite(pixels, 1u, sizeof pixels, stream) != sizeof pixels) return 7;
        }
        fprintf(stderr, "{\"rom_array_payload_bytes\":%zu,\"prepared_workspace_bytes\":%zu,"
                "\"pointer_bytes\":%zu,\"paths\":[%u,%u,%u,%u]}\n", payload,
                sizeof models + sizeof chain, sizeof(void *), (unsigned)chain.path[0],
                (unsigned)chain.path[1], (unsigned)chain.path[2], (unsigned)chain.path[3]);
    }
    return fclose(stream) ? 8 : 0;
}
