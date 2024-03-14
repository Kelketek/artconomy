<template>
  <v-dialog
      v-model="toggle"
      fullscreen
      ref="dialog"
      transition="dialog-bottom-transition"
      :overlay="false"
      scrollable
      :attach="modalTarget"
  >
    <v-card tile class="markdown-help">
      <v-toolbar flat dark color="primary">
        <v-btn icon @click="toggle = false" dark id="close-markdown-help">
          <v-icon :icon="mdiClose"/>
        </v-btn>
        <v-toolbar-title>Formatting Help</v-toolbar-title>
        <v-spacer/>
        <v-toolbar-items>
          <v-btn dark variant="text" @click.prevent="toggle=false">Close</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-text>
        <v-container fluid class="py-0">
          <v-row no-gutters v-if="display" class="markdown-rendered-help">
            <v-col class="text-center" cols="12">
              <h1>Artconomy uses Markdown!</h1>
              <p>Markdown is a language for enhancing your posts with links, lists, and other goodies. Here are some
                examples!</p>
            </v-col>
            <v-col cols="12" md="6" lg="5" offset-lg="1">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Basics</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="6">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="6">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in basicsItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="6"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="6" v-html="md.renderInline(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col cols="12" md="6" lg="5">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Links</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="7" md="8" lg="7">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="5" md="4" lg="5">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in linksItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="5" md="4" lg="5" v-html="md.renderInline(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col class="hide-sm-and-down" cols="12">
              <v-divider></v-divider>
            </v-col>
            <v-col cols="12" md="6" lg="5" offset-lg="1">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Blocks</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12">
                  <p>You can create paragraphs and other 'blocks' of text. Paragraphs should be separated by two
                    newlines.
                    <strong>One new line is not enough!</strong>
                  </p>
                </v-col>
                <v-col cols="6">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="6">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in blocksItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="6"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="6" v-html="md.render(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col cols="12" md="6" lg="4" offset-lg="1">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Lists</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12">
                  <p>You can create numbered and bullet lists. <strong>You don't need to track the numbers
                    yourself!</strong></p>
                  <p>You can also nest paragraphs and other lists by indenting four spaces for each level.</p>
                </v-col>
                <v-col cols="7" md="8" lg="7">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="5" md="4" lg="5">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in listsItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="5" md="4" lg="5" v-html="md.render(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col cols="12" md="5" offset-lg="1">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Headers</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12">
                  <p>You can add headers to your post. Please use these sparingly.
                    <strong>You must start a header at the beginning of a line for this to work.</strong></p>
                </v-col>
                <v-col cols="7" md="8" lg="7">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="5" md="4" lg="5">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in headersItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="5" md="4" lg="5" v-html="md.render(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col cols="12" md="5">
              <v-row no-gutters>
                <v-col cols="12">
                  <span class="title">Extras</span>
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12">
                  <p>Here are a few extra tricks you might find handy!</p>
                </v-col>
                <v-col cols="7" md="8" lg="7">
                  <v-list-subheader class="markdown-table-header">Write</v-list-subheader>
                </v-col>
                <v-col cols="5" md="4" lg="5">
                  <v-list-subheader class="markdown-table-header">...and get</v-list-subheader>
                </v-col>
                <template v-for="(item, index) in extrasItems" :key="index">
                  <v-col cols="12">
                    <v-row no-gutters>
                      <v-col cols="12" class="py-0">
                        <v-divider></v-divider>
                      </v-col>
                      <v-col cols="7" md="8" lg="7"><kbd>{{item.input}}</kbd></v-col>
                      <v-col cols="5" md="4" lg="5" v-html="md.render(item.input)"></v-col>
                    </v-row>
                  </v-col>
                </template>
              </v-row>
            </v-col>
            <v-col cols="12" class="hidden-xs-only text-center mt-4">
              <v-btn color="primary" @click.prevent="toggle = false" variant="flat">Back</v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<style>
.markdown-help .markdown-table-header {
  height: unset;
  padding: 0 !important; }

.markdown-help kbd::before, .markdown-help kbd::after {
  content: unset; }

.markdown-help table.v-datatable.v-table tbody tr td {
  padding: 0 10px; }

.markdown-help table.v-datatable.v-table thead tr th {
  padding: 0 10px; }
</style>

<script setup lang="ts">
import {mdiClose} from '@mdi/js'
import {computed, ref, watch} from 'vue'
import {md} from '@/lib/formattingTools.ts'
import {useTargets} from '@/plugins/targets.ts'

const props = defineProps<{modelValue: boolean}>()
const emit = defineEmits<{'update:modelValue': [value: boolean]}>()
const {modalTarget} = useTargets()

const display = ref(false)
const headers = [
  {
    title: 'Write...',
    sortable: false,
    value: 'input',
  },
  {
    title: 'and get',
    sortable: false,
    value: 'input',
  },
]

const basicsItems = [
  {input: '*Emphasis*'},
  {input: '_Also Emphasis_'},
  {input: '**Strong**'},
  {input: '__Also Strong__'},
  {input: '**Strong and then _Emphasized_**'},
  {input: '___Strong and Emphasized___'},
  {input: '~~Deleted~~'},
  {input: '`code`'},
]

const linksItems = [
  {input: 'https://artconomy.com/'},
  {input: '[A link](https://artconomy.com/)'},
  {input: 'contact@artconomy.com'},
  {input: '[Email us](mailto:contact@artconomy.com)'},
]

const blocksItems = [
  {input: 'This is a test.\nThis is only a test.'},
  {input: 'This is a test.\n\nThis is only a test.'},
  {input: '> This is a block quote.\nIt continues on the next line.\n\nYou need two lines to stop here, too!'},
  {input: '> This is another block quote.\n> \n> We can add blank lines to quotes this way.'},
  {input: '```\n# This is a code block.\n\nfunction greet():\n    print("Hello, world!")\n\ngreet()\n```'},
]

const listsItems = [
  {input: '1. Put on shoes\n1. Tie laces\n1. Grab keys\n1. Forget wallet'},
  {input: '* Fox\n* Wolf\n* Human\n* Elf'},
  {input: '- Fox\n+ Wolf\n+ Human\n- Elf'},
  {
    input: '1. First item\n    * Sub item\n    * Sub item 2\n2. Second item\n\n    ' +
        'This is a test paragraph.\n\n1. Third item',
  },
]

const headersItems = [
  {input: '# Header 1'},
  {input: 'Header 1\n==='},
  {input: '## Header 2'},
  {input: 'Header 2\n---'},
  {input: '### Header 3'},
  {input: '#### Header 4'},
  {input: '##### Header 5'},
  {input: '###### Header 6'},
]

const extrasItems = [
  {
    input: '**Tables**\n\n' +
        '| Headers       | Go            | Here  |\n' +
        '| ------------- |:-------------:| -----:|\n' +
        '| col 3 is      | right-aligned |  $600 |\n' +
        '| col 2 is      | centered      |   $12 |\n' +
        '| zebra stripes | are neat      |    $1 |\n',
  },
  {input: '**Images**\n\n![Artconomy Logo](https://artconomy.com/static/images/logo.png)'},
  {
    input: '**Dividers**\n\nWe thought driving downtown wouldn\'t take that long.\n\n***\n\nThree hours later...' +
        '\n\n---\n\n"Why did we do this again?"',
  },
]

const toggle = computed({
  get: () => {
    return props.modelValue
  },
  set: (val: boolean) => {
    emit('update:modelValue', val)
  }
})

watch(toggle, (val: boolean) => {
  if (val) {
    display.value = true
  }
}, {immediate: true})
</script>
