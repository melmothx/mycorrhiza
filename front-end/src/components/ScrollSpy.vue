<template>
    <main>
        <div>
            <h1>Sticky ScrollSpy Table of Contents in Vue.js</h1>
            <section id="introduction">
                <h2>Introduction</h2>
            </section>
            <section id="about">
                <h2>About Section</h2>
            </section>
            <section id="contact">
                <h2>Contact Section</h2>
            </section>
        </div>
        <nav class="section-nav">
            <ol class="bullet-list">
                <li><a href="#introduction">Introduction</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ol>
        </nav>
    </main>
</template>

<script>
export default {
    data() {
        return {
            observer: null,
        }
    },
    created() {
        this.observer = new IntersectionObserver(this.onElementObserved, {
            root: this.$el,
            threshold: 0.22,
        })
    },
    mounted() {
        this.$el.querySelectorAll('section[id]').forEach((section) => {
            this.observer.observe(section)
        })
    },
    beforeDestroy() {
        this.observer.disconnect()
    },
    methods: {
        onElementObserved(entries) {
            entries.forEach(({ target, isIntersecting }) => {
                const id = target.getAttribute('id')
                if (isIntersecting) {
                    this.$el
                        .querySelector(`nav li a[href="#${id}"]`)
                        .parentElement.classList.add('active')
                } else {
                    this.$el
                        .querySelector(`nav li a[href="#${id}"]`)
                        .parentElement.classList.remove('active')
                }
            })
        },
    },
}
</script>
<style scoped>
/* Sidebar Navigation */
.section-nav {
    margin-top: 2rem;
    padding-left: 0;
    border-left: 1px solid #efefef;
}

.section-nav a {
    text-decoration: none;
    display: block;
    padding: 0.125rem 0;
    color: black;
    transition: all 50ms ease-in-out;
}

.section-nav a:hover,
.section-nav a:focus {
    color: #666;
}

.section-nav li.active > a {
    color: #f2765d;
    font-weight: 500;
}

/* Sticky Navigation */
main > nav {
    position: sticky;
    top: 2rem;
    align-self: start;
}

ul.bullet-list,
ol.bullet-list {
    list-style: none;
    margin: 0;
    padding: 0;
}
li {
    margin-left: 1rem;
}

/** page layout **/
main {
    display: grid;
    grid-template-columns: 1fr 15em;
    max-width: 100em;
    width: 90%;
    margin: 0 auto;
}

/** enlarge the sections for this demo, so that we have a long scrollable page **/
section {
    margin-bottom: 50rem;
}
</style>
