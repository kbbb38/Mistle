#include <string>
#include <system_error>
#include <cerrno>
#include <vector>
#include <fstream>
#include <cstdint>

#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>

/*
    Manages the memory mapping of the fragment ion index
*/
class MappedFragmentIndex
{
    int fd_ = -1;
    void* mapping_ = MAP_FAILED;
    size_t size_ = 0;
    std::vector<uint32_t> bin_counter_;

    public:
        // Non-copyable
        MappedFragmentIndex(const MappedFragmentIndex&) = delete;
        MappedFragmentIndex& operator=(const MappedFragmentIndex&) = delete;

        // Movable
        MappedFragmentIndex(MappedFragmentIndex&& other) noexcept;
        MappedFragmentIndex& operator=(MappedFragmentIndex&& other) noexcept;

        explicit MappedFragmentIndex(const std::string& path);

        ~MappedFragmentIndex()
        {
            cleanup();
        }

        const char* data() const noexcept 
        { 
            return static_cast<const char*>(mapping_); 
        }

        size_t size() const noexcept { return size_; }
        bool empty() const noexcept { return size_ == 0; }
        const std::vector<uint32_t>& bin_count() const noexcept { return bin_counter_; }

        private:
            void cleanup() noexcept
            {
                if (mapping_ != MAP_FAILED && mapping_ != nullptr)
                {
                    munmap(mapping_, size_);
                }
                if (fd_ != -1)
                {
                    close(fd_);
                }
            }
};