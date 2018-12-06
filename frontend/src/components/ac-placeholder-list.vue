<template>
  <v-container grid-list-lg class="placeholder-list">
    <v-layout row wrap>
      <v-flex xs12 sm4 lg3
              v-for="placeholder in growing"
              :key="placeholder.id"
              @click="currentPlaceholder = placeholder"
              class="clickable"
      >
        <v-card>
          <v-card-title primary-title v-html="renderInline(placeholder.title + '')" ></v-card-title>
          <v-card-text>
            <ul>
              <li><strong>Task Weight:</strong> {{placeholder.task_weight}}</li>
              <li><strong>Expected Turnaround:</strong> {{placeholder.expected_turnaround}} days</li>
            </ul>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <v-dialog v-model="showDialog" max-width="80%">
      <v-card v-if="showDialog">
        <v-card-title class="clickable" v-if="editing" @click="editing=false"><v-icon>lock_open</v-icon></v-card-title>
        <v-card-title class="clickable" v-else @click="editing=true"><v-icon>lock</v-icon></v-card-title>
        <v-card-title>
          <ac-patchfield v-model="currentPlaceholder.title" name="title" :editmode="editing" :url="currentUrl" />
        </v-card-title>
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs6>
              <strong>Task weight:</strong>
            </v-flex>
            <v-flex xs6>
              <ac-patchfield v-model="currentPlaceholder.task_weight" name="task_weight" :editmode="editing" :url="currentUrl" />
            </v-flex>
            <v-flex xs6>
              <strong>Days turnaround:</strong>
            </v-flex>
            <v-flex xs6>
              <ac-patchfield v-model="currentPlaceholder.expected_turnaround" name="expected_turnaround" :editmode="editing" :url="currentUrl" />
            </v-flex>
            <v-flex xs12><strong>Description:</strong></v-flex>
          </v-layout>
          <ac-patchfield v-model="currentPlaceholder.description" name="description" :multiline="true" :editmode="editing" :url="currentUrl" />
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" flat @click.stop="showDialog=false">Close</v-btn>
          <ac-action
              variant="danger" :confirm="true" :success="postDelete"
              :url="currentUrl"
              method="DELETE"
              dark color="red"
          > Delete
            <div class="text-left" slot="confirmation-text">Are you sure you wish to delete this placeholder sale? This cannot be undone!</div>
          </ac-action>
          <ac-action
              variant="danger" :confirm="true" :success="fetchItems"
              :url="currentUrl"
              method="PATCH"
              dark color="primary"
              :send="{status: 8}"
              v-if="currentPlaceholder.status === 4"
          >
            Mark Completed
          </ac-action>
          <ac-action
              variant="danger" :confirm="true" :success="fetchItems"
              :url="currentUrl"
              method="PATCH"
              dark color="primary"
              :send="{status: 4}"
              v-else
          >
            Reopen
          </ac-action>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-btn
           dark
           color="green"
           fab
           hover
           fixed
           right
           bottom
           large
           @click="showNew=true"
    >
      <v-icon x-large>add</v-icon>
    </v-btn>
    <ac-form-dialog title="New Placeholder Sale" submit-text="Create" v-model="showNew"
                    ref="newPlaceholderForm" :schema="newPlaceholderSchema" :model="newPlaceholderModel"
                    :options="newPlaceholderOptions" :success="addPlaceholder"
                    :url="url"
    />
  </v-container>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import Paginated from '../mixins/paginated'
  import AcPatchfield from './ac-patchfield'
  import Editable from '../mixins/editable'
  import {md, EventBus} from '../lib'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormDialog from './ac-form-dialog'
  export default {
    name: 'ac-placeholder-list',
    components: {AcFormDialog, AcPatchfield},
    props: ['url'],
    mixins: [Viewer, Perms, Paginated, Editable],
    data () {
      return {
        currentPlaceholder: false,
        showNew: false,
        newPlaceholderModel: {
          title: '',
          description: '',
          expected_turnaround: 1,
          task_weight: 1
        },
        newPlaceholderSchema: {
          fields: [{
            type: 'v-text',
            label: 'Order Title',
            model: 'title',
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Expected Turnaround (days)',
            model: 'expected_turnaround',
            step: '1',
            min: '1',
            hint: (
              'How many days you expect this task to take to complete. May be used in calculations to let customers ' +
              'know how long your current expected wait time is.'
            ),
            featured: true,
            required: true
          }, {
            type: 'v-text',
            inputType: 'number',
            label: 'Task Weight',
            model: 'task_weight',
            step: '1',
            min: '1',
            hint: (
              'How much this order will contribute to your load. If your maximum load, as set in your settings, ' +
              'is exceeded, commissioners will not be able to place new orders.'
            ),
            featured: true,
            required: true
          }, {
            type: 'v-text',
            label: 'Description',
            model: 'description',
            multiLine: true,
            featured: true,
            required: true,
            validator: VueFormGenerator.validators.string,
            hint: (
              'Place all of your notes you need to keep track of this order here.'
            )
          }]
        },
        newPlaceholderOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      renderInline (text) {
        // Issues with 'this' scoping
        return `<span>${md.renderInline(text)}</span>`
      },
      addPlaceholder (response) {
        this.growing.push(response)
        this.currentPlaceholder = this.growing[this.growing.length - 1]
        this.showNew = false
        EventBus.$emit('refresh-sales-stats')
      },
      postDelete () {
        let index = this.growing.indexOf(this.currentPlaceholder)
        if (index > -1) {
          this.growing.splice(index, 1)
        }
        this.showDialog = false
        this.currentPlaceholder = null
        EventBus.$emit('refresh-sales-stats')
      }
    },
    computed: {
      showDialog: {
        get () {
          return Boolean(this.currentPlaceholder)
        },
        set () {
          // Should only ever be set false.
          this.currentPlaceholder = null
        }
      },
      currentUrl () {
        return `/api/sales/v1/account/${this.username}/sales/placeholder/${this.currentPlaceholder.id}/`
      }
    }
  }
</script>

<style>
</style>