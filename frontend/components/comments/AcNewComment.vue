<template>
  <v-card :class="{alternate, comment: true, 'elevation-3': alternate}" class="new-comment">
    <v-toolbar dense v-if="isRegistered || (isLoggedIn && guestOk)">
      <ac-avatar :user="viewer" :show-name="false"></ac-avatar>
      <v-toolbar-title>{{viewerName}}</v-toolbar-title><v-spacer></v-spacer>
    </v-toolbar>
    <v-card-text>
      <v-layout row wrap v-if="!isRegistered && !guestOk">
        <v-flex xs12 text-xs-center>
          <v-btn @click="editing=true" class="new-comment-button" :to="{name: 'Login', params: {tabName: 'login'}, query: {next: this.$route.fullPath}}">Log in or Register to
            Comment!
          </v-btn>
        </v-flex>
      </v-layout>
      <v-subheader v-else-if="!value">New Comment</v-subheader>
      <v-layout row wrap v-if="isRegistered || (isLoggedIn && guestOk)">
        <v-flex xs12 sm12>
          <ac-form-container v-bind="newCommentForm.bind">
            <v-form @submit.prevent="publish">
              <ac-bound-field :field="newCommentForm.fields.text" field-type="ac-editor">
                <v-flex text-xs-right slot="actions">
                  <v-layout wrap>
                    <v-spacer></v-spacer>
                    <v-flex shrink v-if="value">
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn v-on="on" @click="cancel" color="danger" icon class="cancel-button">
                            <v-icon>cancel</v-icon>
                          </v-btn>
                        </template>
                        <span>Cancel</span>
                      </v-tooltip>
                    </v-flex>
                    <v-flex shrink>
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-btn v-on="on" color="primary" type="submit" icon class="submit-button">
                          <v-icon>send</v-icon>
                        </v-btn>
                      </template>
                      <span>Send</span>
                    </v-tooltip>
                    </v-flex>
                  </v-layout>
                </v-flex>
              </ac-bound-field>
            </v-form>
          </ac-form-container>
        </v-flex>
      </v-layout>
    </v-card-text>
  </v-card>
</template>

<style lang="stylus" scoped>
  .theme--dark .comment.alternate {
    background-color: var(--v-darkBase-darken2)
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
import AcEditor from '../fields/AcEditor.vue'
import {ListController} from '@/store/lists/controller'
import {Prop} from 'vue-property-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {flatten} from '@/lib'

  @Component({
    components: {AcBoundField, AcFormContainer, AcAvatar, AcEditor},
  })
export default class AcNewComment extends mixins(Viewer) {
    @Prop({required: true})
    public commentList!: ListController<Comment>
    @Prop({default: false})
    public alternate!: boolean
    @Prop({default: false})
    public value!: boolean
    @Prop({default: false})
    public guestOk!: boolean
    public newCommentForm: FormController = null as unknown as FormController

    // Used for when we're nested under a comment thread.
    public cancel() {
      this.$emit('input', false)
    }

    public publish() {
      this.newCommentForm.submit().then(this.commentList.push).then(this.cancel).catch(this.newCommentForm.setErrors)
    }

    public created() {
      this.newCommentForm = this.$getForm(flatten(this.commentList.name) + '_new', {
        endpoint: this.commentList.endpoint, fields: {text: {value: ''}},
      })
    }
}
</script>
