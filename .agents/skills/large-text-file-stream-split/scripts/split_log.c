/*
 * split_log.c
 * ------------------------------------------------------------------
 * Stream-splits a very large text file into N byte-exact chunks,
 * cutting only on LF (\n) boundaries so concatenating the chunks in
 * name order reproduces the source byte-for-byte.
 *
 * Per-part target size is dynamic: remaining_bytes / remaining_parts,
 * recomputed each time a new part is opened. This self-corrects for
 * the "cut at first LF after threshold" overshoot, so we land on
 * EXACTLY N parts of similar size.
 *
 * Output (in <out_dir>):
 *   <base>_part_NNN_of_TTT__lines_SSSSSSS-EEEEEEE.txt
 *   INDEX.csv
 *
 * Usage:
 *   split_log <source_file> <out_dir> [parts] [base_name]
 *
 * Defaults:
 *   parts     = 100
 *   base_name = "part" (used in chunk filenames)
 *
 * Build (any C89/C99 compiler — MSVC / gcc / clang / MinGW / tcc):
 *   cl    /O2 /W4 /MT /Fe:split_log.exe split_log.c
 *   gcc   -O2 -Wall -o split_log.exe split_log.c          (Linux/macOS: drop .exe)
 *   clang -O2 -Wall -o split_log.exe split_log.c
 *
 * Portability:
 *   - C standard library only (stdio/stdlib/string/stdint/sys/stat).
 *   - 64-bit file offsets: _FILE_OFFSET_BITS=64 + _fseeki64/_ftelli64 on Windows,
 *     fseeko/ftello on POSIX.
 *   - mkdir: _mkdir on Windows, mkdir(path, 0755) on POSIX.
 *   - On non-Windows shells, quote '#194.txt' (# is a comment char).
 *
 * ------------------------------------------------------------------
 */

#define _CRT_SECURE_NO_WARNINGS
#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>

#ifdef _WIN32
  #include <direct.h>
  #include <io.h>
  #define MKDIR(p) _mkdir(p)
  #define FSEEK64(f,o,w) _fseeki64((f),(o),(w))
  #define FTELL64(f)     _ftelli64((f))
  typedef __int64 i64;
#else
  #include <sys/types.h>
  #define MKDIR(p) mkdir((p), 0755)
  #define FSEEK64(f,o,w) fseeko((f),(o),(w))
  #define FTELL64(f)     ftello((f))
  typedef long long i64;
#endif

#define BUF_SIZE (4 * 1024 * 1024)  /* 4 MiB read buffer */

static int digit_count(int n) {
    int d = 1; while (n >= 10) { n /= 10; d++; } return d;
}

static i64 file_size(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return -1;
    if (FSEEK64(f, 0, SEEK_END) != 0) { fclose(f); return -1; }
    i64 sz = FTELL64(f);
    fclose(f);
    return sz;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr,
            "Usage: %s <source_file> <out_dir> [parts=100] [base_name=part]\n",
            argv[0]);
        return 2;
    }
    const char *src      = argv[1];
    const char *out_dir  = argv[2];
    int   parts          = (argc >= 4) ? atoi(argv[3]) : 100;
    const char *base     = (argc >= 5) ? argv[4] : "part";

    if (parts < 1) { fprintf(stderr, "parts must be >= 1\n"); return 2; }

    i64 total = file_size(src);
    if (total < 0) {
        fprintf(stderr, "ERROR: cannot stat source: %s\n", src);
        return 1;
    }

    /* mkdir -p (one level; caller responsible for parents) */
    MKDIR(out_dir);

    FILE *in = fopen(src, "rb");
    if (!in) { fprintf(stderr, "ERROR: cannot open source: %s\n", src); return 1; }

    /* INDEX.csv */
    char idx_path[2048];
    snprintf(idx_path, sizeof(idx_path), "%s/INDEX.csv", out_dir);
    FILE *idx = fopen(idx_path, "wb");
    if (!idx) { fprintf(stderr, "ERROR: cannot create %s\n", idx_path); fclose(in); return 1; }
    fprintf(idx, "Part,FileName,StartLine,EndLine,LineCount,StartByte,EndByte,ByteSize\n");

    unsigned char *buf = (unsigned char*)malloc(BUF_SIZE);
    if (!buf) { fprintf(stderr, "ERROR: OOM\n"); fclose(in); fclose(idx); return 1; }

    int pad = digit_count(parts);

    i64 byte_pos              = 0;
    i64 bytes_written_part    = 0;
    i64 part_start_byte       = 0;
    i64 part_target           = 0;
    int part_num              = 0;
    int part_start_line       = 1;
    int part_lines            = 0;
    int global_line           = 1;   /* 1-based; line N starts after (N-1)-th LF */

    /* Open first part */
    char tmp_path[2048];
    FILE *out = NULL;

    #define OPEN_NEXT_PART() do {                                                  \
        part_num++;                                                                \
        i64 remaining_parts = parts - part_num + 1;                                \
        i64 remaining_bytes = total - byte_pos;                                    \
        part_target = (remaining_parts <= 1)                                       \
            ? (i64)0x7fffffffffffffffLL                                            \
            : (remaining_bytes + remaining_parts - 1) / remaining_parts;           \
        snprintf(tmp_path, sizeof(tmp_path),                                       \
                 "%s/%s_part_%0*d_of_%0*d__OPEN.tmp",                              \
                 out_dir, base, pad, part_num, pad, parts);                        \
        out = fopen(tmp_path, "wb");                                               \
        if (!out) { fprintf(stderr, "ERROR: cannot create %s\n", tmp_path);        \
                    free(buf); fclose(in); fclose(idx); return 1; }                \
        part_start_byte    = byte_pos;                                             \
        part_start_line    = global_line;                                          \
        part_lines         = 0;                                                    \
        bytes_written_part = 0;                                                    \
    } while (0)

    #define CLOSE_PART() do {                                                      \
        fflush(out); fclose(out); out = NULL;                                      \
        int end_line = (part_lines == 0)                                           \
            ? part_start_line                                                      \
            : part_start_line + part_lines - 1;                                    \
        char final_path[2048];                                                     \
        snprintf(final_path, sizeof(final_path),                                   \
                 "%s/%s_part_%0*d_of_%0*d__lines_%07d-%07d.txt",                   \
                 out_dir, base, pad, part_num, pad, parts,                         \
                 part_start_line, end_line);                                       \
        if (rename(tmp_path, final_path) != 0) {                                   \
            fprintf(stderr, "ERROR: rename %s -> %s failed\n",                     \
                    tmp_path, final_path);                                         \
        }                                                                          \
        const char *bn = strrchr(final_path, '/');                                 \
        bn = bn ? bn + 1 : final_path;                                             \
        fprintf(idx, "%d,%s,%d,%d,%d,%lld,%lld,%lld\n",                            \
                part_num, bn, part_start_line, end_line,                           \
                end_line - part_start_line + 1,                                    \
                (long long)part_start_byte,                                        \
                (long long)(byte_pos - 1),                                         \
                (long long)bytes_written_part);                                    \
    } while (0)

    OPEN_NEXT_PART();

    size_t n;
    while ((n = fread(buf, 1, BUF_SIZE, in)) > 0) {
        size_t off = 0;
        while (off < n) {
            int need_cut = (bytes_written_part >= part_target) && (part_num < parts);
            if (need_cut) {
                /* find next LF in buf[off..n) */
                size_t lf = (size_t)-1;
                for (size_t i = off; i < n; i++) {
                    if (buf[i] == 0x0A) { lf = i; break; }
                }
                if (lf != (size_t)-1) {
                    size_t chunk = (lf - off + 1);
                    fwrite(buf + off, 1, chunk, out);
                    bytes_written_part += (i64)chunk;
                    part_lines++; global_line++;
                    off      += chunk;
                    byte_pos += (i64)chunk;
                    CLOSE_PART();
                    OPEN_NEXT_PART();
                    continue;
                }
                /* no LF in remaining buffer; fall through, write all */
            }
            /*
             * Compute how many bytes we MAY write without overshooting the
             * current part's target. When the remaining target gap is smaller
             * than the buffer's remaining bytes, write only the gap; the next
             * iteration will see need_cut == true and scan for the LF.
             * Without this cap, small files (or large files with parts smaller
             * than BUF_SIZE) would never trigger a cut and would produce a
             * single huge chunk.
             */
            size_t avail = n - off;
            size_t chunk = avail;
            if (part_num < parts) {
                i64 gap = part_target - bytes_written_part;
                if (gap > 0 && (i64)chunk > gap) {
                    chunk = (size_t)gap;
                }
            }
            fwrite(buf + off, 1, chunk, out);
            for (size_t i = off; i < off + chunk; i++) {
                if (buf[i] == 0x0A) { part_lines++; global_line++; }
            }
            bytes_written_part += (i64)chunk;
            byte_pos           += (i64)chunk;
            off                += chunk;
        }
    }

    /* Close final part */
    CLOSE_PART();

    free(buf);
    fclose(in);
    fclose(idx);

    fprintf(stdout, "Wrote %d chunks. Total %lld bytes (source: %lld bytes).\n",
            part_num, (long long)byte_pos, (long long)total);
    return (byte_pos == total) ? 0 : 1;
}
