<template>
  <v-dialog
      v-model="toggle"
      fullscreen
      ref="dialog"
      transition="dialog-bottom-transition"
      :overlay="false"
      scrollable
  >
    <v-card tile>
      <v-toolbar card dark color="primary">
        <v-btn icon @click.native="toggle = false" dark>
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Formatting Help</v-toolbar-title>
        <v-spacer />
        <v-toolbar-items>
          <v-btn dark flat @click.prevent="toggle=false">Close</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-layout row wrap>
          <v-flex xs12>
            <h1>Artconomy uses Markdown!</h1>
            <p>Markdown is a language for enhancing your posts with links, lists, and other goodies. Here are some examples!</p>
            <p><code>*Italics*</code> produces <em>Italics</em></p>
            <p><code>**Bold**</code> produces <strong>Bold</strong></p>
            <p><code>***Bold Italics***</code> produces <strong><em>Bold Italics</em></strong></p>
            <p><code>`Code`</code> produces <code>Code</code></p>
            <p><code>[A Link](https://artconomy.com/)</code> produces <a href="https://artconomy.com">A Link</a></p>
            <p><code>&lt;support@artconomy.com&gt;</code></p> produces <a href="mailto:support@artconomy.com">support@artconomy.com</a>
            <p>Paragraphs should be separated by two newlines. <strong>One new line is not enough!</strong></p>
            <code>
              This is a test.
              This is only a test
            </code>
            <p><strong>...produces...</strong></p>
            <p>This is a test. This is only a test.</p>
            <p><strong>Whereas...</strong></p>
            <p><code>
              This is a test.

              This is only a test.
            </code></p>
            <p><strong>...produces...</strong></p>
            <p>This is a test.</p>
            <p>This is only a test.</p>
            <v-divider />
            <h2>Lists</h2>
            <p><code>
              * Fox
              * Wolf
              * Human
              * Elf
            </code></p>
            <p><strong>...produces...</strong></p>
            <ul>
              <li>Fox</li>
              <li>Wolf</li>
              <li>Human</li>
              <li>Elf</li>
            </ul>
            <p><code>
              1. Put on Shoes
              1. Tie Laces
              1. Grab Keys
              1. Forget wallet
            </code></p>
            <p><strong>...produces...</strong></p>
            <ol>
              <li>Put on Shoes</li>
              <li>Tie Laces</li>
              <li>Grab Keys</li>
              <li>Forget wallet</li>
            </ol>
            <v-divider />
            <h2>Headers</h2>
            <p>You can even add headers into your posts! <strong>Please use these sparingly.</strong></p>
            <p><code># Header 1</code></p>
            <h1>Header 1</h1>
            <p><code>## Header 2</code></p>
            <h2>Header 2</h2>
            <p><code>### Header 3</code></p>
            <h3>Header 3</h3>
            <p><code>#### Header 4</code></p>
            <h4>Header 4</h4>
            <p><code>##### Header 5</code></p>
            <h5>Header 5</h5>
            <p><code>####6 Header 6</code></p>
            <h6>Header 6</h6>
            <p>If you need to show off some code, you can also do:</p>
            <p><code>
              ```
              def hello_world(message):
              print(message)

              hello_world("O hai!")
              ```
            </code></p>
            <p><strong>...which produces...</strong></p>
            <p><code>
              def hello_world(message):
              print(message)

              hello_world("O hai!")
            </code></p>

          </v-flex>
          <v-flex xs12 text-xs-center mt-4 class="hidden-xs-only">
            <v-btn color="primary" @click.prevent="toggle = false">Back</v-btn>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
  export default {
    name: 'ac-markdown-explanation',
    props: ['value'],
    computed: {
      toggle: {
        get () {
          return this.value
        },
        set (value) {
          this.$emit('input', value)
        }
      }
    }
  }
</script>