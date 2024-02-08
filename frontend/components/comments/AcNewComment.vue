<template>
  <v-card :class="{comment: true, 'elevation-3': alternate}" class="new-comment" :color="color">
    <v-toolbar dense color="black" v-if="isRegistered || (isLoggedIn && guestOk)">
      <ac-avatar :user="viewer" :show-name="false" class="ml-3"/>
      <v-toolbar-title class="ml-1">
        <ac-link :to="profileLink(viewer as User)">{{viewerName}}</ac-link>
      </v-toolbar-title>
      <v-spacer/>
    </v-toolbar>
    <v-card-text>
      <v-row no-gutters v-if="!isRegistered && !guestOk">
        <v-col class="text-center" cols="12">
          <v-btn class="new-comment-button"
                 :to="{name: 'Login', query: {next: $route.fullPath}}"
                 variant="elevated"
          >Log in or
            Register to
            Comment!
          </v-btn>
        </v-col>
      </v-row>
      <v-list-subheader v-else-if="!modelValue">New Comment</v-list-subheader>
      <v-row no-gutters v-if="isRegistered || (isLoggedIn && guestOk)">
        <v-col cols="12" sm="12">
          <ac-form-container v-bind="newCommentForm.bind">
            <ac-form @submit.prevent="publish">
              <ac-bound-field :field="newCommentForm.fields.text" field-type="ac-editor">
                <template v-slot:actions>
                  <v-col class="text-right">
                    <v-row dense>
                      <v-spacer/>
                      <v-col class="shrink" v-if="modelValue">
                        <v-tooltip top>
                          <template v-slot:activator="{ props }">
                            <v-btn v-bind="props" @click="cancel" color="danger" icon small class="cancel-button">
                              <v-icon icon="mdi-cancel"/>
                            </v-btn>
                          </template>
                          <span>Cancel</span>
                        </v-tooltip>
                      </v-col>
                      <v-col class="shrink">
                        <v-tooltip top>
                          <template v-slot:activator="{ props }">
                            <v-btn v-bind="props" color="blue" type="submit" icon class="submit-button" small>
                              <v-icon icon="mdi-send"/>
                            </v-btn>
                          </template>
                          <span>Send</span>
                        </v-tooltip>
                      </v-col>
                    </v-row>
                  </v-col>
                </template>
              </ac-bound-field>
            </ac-form>
          </ac-form-container>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style lang="stylus" scoped>
.theme--dark .comment.alternate {
  background-color: var(--v-well-darken-2)
}
</style>

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import AcEditor from '../fields/AcEditor.vue'
import {ListController} from '@/store/lists/controller.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting.ts'
import {RawData} from '@/store/forms/types/RawData.ts'
import {User} from '@/store/profiles/types/User.ts'

@Component({
  components: {
    AcLink,
    AcForm,
    AcBoundField,
    AcFormContainer,
    AcAvatar,
    AcEditor,
  },
  emits: ['update:modelValue'],
})
class AcNewComment extends mixins(Viewer, Formatting) {
  @Prop({required: true})
  public commentList!: ListController<Comment>

  @Prop({default: false})
  public alternate!: boolean

  @Prop({default: false})
  public modelValue!: boolean

  @Prop({default: false})
  public guestOk!: boolean

  @Prop({default: () => ({})})
  public extraData!: RawData

  public newCommentForm: FormController = null as unknown as FormController

  public get color() {
    if (this.alternate) {
      // @ts-ignore
      return this.$vuetify.theme.current.colors['well-darken-4']
    }
    return ''
  }

  // Used for when we're nested under a comment thread.
  public cancel() {
    this.$emit('update:modelValue', false)
  }

  @Watch('extraData', {deep: true})
  public updateData() {
    this.newCommentForm.fields.extra_data.update(this.extraData)
  }

  public publish() {
    this.newCommentForm.submit().then(this.commentList.push).then(this.cancel).catch(this.newCommentForm.setErrors)
  }

  public created() {
    this.newCommentForm = this.$getForm(this.commentList.name + '_new', {
      endpoint: this.commentList.endpoint,
      fields: {
        text: {value: ''},
        extra_data: {value: this.extraData},
      },
    })
  }
}

export default toNative(AcNewComment)
</script>
